# -*- coding: utf-8 -*-
"""Cactus Revenge - real-time 3D Python game built with Panda3D."""
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton, DirectLabel
from direct.task import Task
from panda3d.core import (AmbientLight, DirectionalLight, Vec4, Vec3, Point3,
                          CardMaker, TextNode, WindowProperties)
from panda3d.core import CollisionTraverser, CollisionNode, CollisionSphere, CollisionHandlerQueue
from random import uniform, choice

class CactusRevenge(ShowBase):
    def __init__(self):
        super().__init__()
        props = WindowProperties(); props.setTitle('انتقام الصبار'); props.setSize(1280, 720)
        self.win.requestProperties(props)
        self.setBackgroundColor(0.94, 0.67, 0.43, 1)
        self.disableMouse()
        self.camera.setPos(0, -18, 8)
        self.camera.lookAt(0, 0, 1.8)
        self.setFrameRateMeter(False)
        self.score = 0; self.best = 0; self.speed = 7.0
        self.running = False; self.jump_v = 0; self.air = False
        self.ammo = 3; self.ammo_timer = 0; self.shield_timer = 0; self.spawn_timer = 1.4
        self.enemies = []; self.spikes = []; self.keys = {}
        self.setup_lights(); self.setup_world(); self.setup_cactus()
        self.setup_ui(); self.accept('space', self.jump); self.accept('arrow_up', self.jump)
        self.accept('x', self.activate_shield); self.accept('f', self.activate_shield)
        self.accept('enter', self.start_game)
        for key in ['space','arrow_up','x','f']:
            self.accept(key+'-repeat', getattr(self, {'space':'jump','arrow_up':'jump','x':'activate_shield','f':'activate_shield'}[key]))
        self.taskMgr.add(self.update, 'game-update')

    def setup_lights(self):
        amb = AmbientLight('ambient'); amb.setColor(Vec4(.65,.57,.48,1)); self.render.setLight(self.render.attachNewNode(amb))
        sun = DirectionalLight('sun'); sun.setColor(Vec4(1,.83,.66,1))
        sn = self.render.attachNewNode(sun); sn.setHpr(-35,-55,0); self.render.setLight(sn)

    def cube(self, parent, name, pos, scale, color):
        n = self.loader.loadModel('models/box'); n.reparentTo(parent); n.setName(name)
        n.setPos(*pos); n.setScale(*scale); n.setColor(*color); n.setTextureOff(1); return n

    def sphere(self, parent, name, pos, scale, color):
        n = self.loader.loadModel('models/misc/sphere'); n.reparentTo(parent); n.setName(name)
        n.setPos(*pos); n.setScale(*scale); n.setColor(*color); n.setTextureOff(1); return n

    def setup_world(self):
        self.cube(self.render,'sand',(0,0,-.28),(60,60,.25),(.72,.43,.22,1))
        # Distant low-poly mountains
        for i in range(13):
            x=-28+i*4.8
            m=self.loader.loadModel('models/misc/rgbCube'); m.reparentTo(self.render)
            m.setPos(x,18,1.4); m.setScale(uniform(1.5,3),2,uniform(2,4)); m.setColor(*( (.62,.37,.29,1) if i%2 else (.72,.45,.32,1) ))
        # Sun and desert rocks
        self.sphere(self.render,'sun',(12,24,13),(2.4,2.4,2.4),(1,.88,.62,1))
        for i in range(24):
            self.sphere(self.render,'rock',(uniform(-28,28),uniform(4,22),-.03),(.25,.22,.16),(.42,.27,.19,1))
        # Lane markers
        self.lane=[]
        for i in range(20):
            b=self.cube(self.render,'lane-marker',(-20+i*2.2,0,-.12),(.65,.06,.025),(.91,.62,.36,1)); self.lane.append(b)

    def setup_cactus(self):
        self.cactus=self.render.attachNewNode('cactus-player')
        green=(.15,.55,.29,1); light=(.32,.72,.39,1)
        self.cube(self.cactus,'body',(0,0,1.05),(.48,.42,1.08),green)
        self.sphere(self.cactus,'crown',(0,0,2.03),(.48,.42,.48),green)
        self.cube(self.cactus,'left-arm',(-.58,0,1.22),(.17,.17,.55),green)
        self.cube(self.cactus,'left-arm-top',(-.45,0,1.62),(.17,.17,.42),green)
        self.cube(self.cactus,'right-arm',(.58,0,1.02),(.17,.17,.47),green)
        self.cube(self.cactus,'right-arm-top',(.45,0,1.38),(.17,.17,.38),green)
        for x in [-.2, .2]:
            self.sphere(self.cactus,'eye',(x,-.405,1.63),(.095,.04,.12),(1,1,1,1))
            self.sphere(self.cactus,'pupil',(x+.02,-.445,1.63),(.04,.025,.055),(.04,.12,.07,1))
        self.cactus.setPos(-3,0,0)
        self.cactus.setTag('kind','player')
        self.shield = self.sphere(self.cactus,'protective-shield',(0,0,1.05),(1.15,.9,1.45),(.18,.82,1,.28))
        self.shield.setTransparency(True); self.shield.hide()

    def setup_ui(self):
        self.hud=DirectLabel(text='⭐ 0     🏆 0     🌵 3/3', scale=.065, pos=(0,0,.91),
            text_fg=(.1,.12,.16,1), frameColor=(.88,.91,.92,.78), frameSize=(-5.4,5.4,-.55,.65))
        self.title=DirectLabel(text='🌵 انتقام الصبار', scale=.12, pos=(0,0,.18), text_fg=(.05,.16,.22,1), frameColor=(0,0,0,0))
        self.info=DirectLabel(text='اقفز فوق الديناصورات واستخدم درع الحماية', scale=.055, pos=(0,0,.04), text_fg=(1,1,1,1), frameColor=(0,0,0,0))
        self.start_btn=DirectButton(text='ابدأ التحدي', scale=.085, pos=(0,0,-.12), command=self.start_game,
            frameColor=(.12,.75,.48,1), text_fg=(.02,.08,.08,1))
        self.jump_btn=DirectButton(text='قفز', scale=.08, pos=(-1.05,0,-.82), command=self.jump,
            frameColor=(.0,.52,.78,1), text_fg=(1,1,1,1))
        self.shoot_btn=DirectButton(text='درع حماية', scale=.08, pos=(1.05,0,-.82), command=self.activate_shield,
            frameColor=(.82,.38,.05,1), text_fg=(1,1,1,1))

    def start_game(self):
        for e in self.enemies: e['node'].removeNode()
        for s in self.spikes: s['node'].removeNode()
        self.enemies.clear(); self.spikes.clear()
        self.score=0; self.speed=7; self.ammo=3; self.ammo_timer=0; self.spawn_timer=1.3
        self.cactus.setZ(0); self.jump_v=0; self.air=False; self.running=True
        self.title.hide(); self.info.hide(); self.start_btn.hide(); self.update_hud()

    def jump(self):
        if self.running and not self.air:
            self.air=True; self.jump_v=10.5

    def activate_shield(self):
        if not self.running or self.ammo<=0: return
        self.ammo-=1
        self.shield_timer=1.8
        self.shield.show()
        self.update_hud()

    def spawn_enemy(self):
        root=self.render.attachNewNode('dinosaur')
        kind=choice(['small','small','large']); size=1.0 if kind=='small' else 1.35
        red=(.62,.22,.20,1) if kind=='small' else (.85,.38,.12,1)
        self.sphere(root,'body',(0,0,.85),(.78,.48,.52),red)
        self.sphere(root,'head',(-.66,-.02,1.35),(.43,.38,.42),red)
        self.sphere(root,'snout',(-.96,-.12,1.16),(.32,.32,.19),red)
        self.cube(root,'belly',(0,-.39,.58),(.55,.06,.2),(.9,.72,.49,1))
        self.sphere(root,'eye',(-.78,-.36,1.48),(.08,.045,.09),(1,.95,.8,1))
        self.cube(root,'tail',(.85,0,.78),(.58,.16,.15),red)
        for x in [-.3,.35]: self.cube(root,'leg',(x,0,.2),(.18,.2,.38),red)
        root.setScale(size); root.setPos(13,0,0)
        self.enemies.append({'node':root,'kind':kind,'size':size,'hit':False})

    def update_hud(self):
        self.hud['text']=f'⭐ {int(self.score)}     🏆 {self.best}     🛡️ {self.ammo}/3'

    def finish(self):
        self.running=False; self.best=max(self.best,int(self.score))
        self.title['text']='انتهت الجولة!'
        self.info['text']=f'نتيجتك: {int(self.score)}   |   أفضل نتيجة: {self.best}'
        self.title.show(); self.info.show(); self.start_btn['text']='حاول مجدداً'; self.start_btn.show(); self.update_hud()

    def update(self, task):
        dt=min(globalClock.getDt(),.05)
        if self.running:
            self.score+=dt*12; self.speed=min(14,self.speed+dt*.045)
            if self.air:
                z=self.cactus.getZ()+self.jump_v*dt; self.jump_v-=27*dt
                if z<=0: z=0; self.air=False
                self.cactus.setZ(z)
            self.spawn_timer-=dt
            if self.spawn_timer<=0:
                self.spawn_enemy(); self.spawn_timer=uniform(1.2,1.9)*(7/self.speed)
            for e in list(self.enemies):
                n=e['node']; n.setX(n.getX()-self.speed*dt)
                if not e['hit'] and abs(n.getX()+3)<.95 and self.cactus.getZ()<.85:
                    if self.shield_timer > 0:
                        e['hit']=True; n.removeNode(); self.enemies.remove(e); self.score += 20
                    else:
                        self.finish(); break
                if n.getX() < -14:
                    n.removeNode(); self.enemies.remove(e); self.score+=10
            if self.shield_timer > 0:
                self.shield_timer -= dt
                if self.shield_timer <= 0: self.shield.hide()
            self.ammo_timer+=dt
            if self.ammo<3 and self.ammo_timer>3.2: self.ammo+=1; self.ammo_timer=0
            for b in self.lane:
                b.setX(b.getX()-self.speed*dt)
                if b.getX()<-22: b.setX(22)
            self.update_hud()
        return Task.cont

app=CactusRevenge(); app.run()
