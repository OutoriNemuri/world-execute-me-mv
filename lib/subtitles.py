# -*- coding: utf-8 -*-
"""subtitles — Chinese translations, keyed by the English lyric line.

The video shows the English original (with the sung word highlighted) plus the
Chinese line beneath it.  These are singable-equivalent translations, not
literal ones.
"""

ZH = {
    "Switch on the power line":
        "接通电源线",
    "Remember to put on protection":
        "记得做好防护",
    "Lay down your pieces":
        "摆好你的棋子",
    "And let's begin object creation":
        "让我们开始创建对象",
    "Fill in my data parameters":
        "填好我的数据参数",
    "Initialization":
        "初始化",
    "Set up our new world":
        "搭建我们的新世界",
    "And let's begin the simulation":
        "让我们开始这场模拟",

    "If I'm a set of point":
        "如果我是一组点",
    "Then I will give you my dimension":
        "那我将给你我的维度",
    "If I'm a circle":
        "如果我是一个圆",
    "Then I will give you my circumference":
        "那我将给你我的周长",
    "If I'm a sine wave":
        "如果我是一道正弦波",
    "Then you can sit on all my tangents":
        "那你就能坐在我所有的切线上",
    "If I approach infinity":
        "如果我趋近于无穷",
    "Then you can be my limitations":
        "那你就可以成为我的极限",

    "Switch my current":
        "切换我的电流",
    "To AC, to DC":
        "交流，直流",
    "And then blind my vision":
        "再蒙上我的视线",
    "So dizzy, so dizzy":
        "好晕，好晕",
    "Oh, we can travel":
        "啊，我们可以穿行",
    "To AD, to BC":
        "去公元后，去公元前",
    "And we can unite":
        "我们可以合为一体",
    "So deeply, so deeply":
        "如此深，如此深",

    "If I can, if I can":
        "如果我能，如果我能",
    "Give you all the simulations":
        "给你所有的模拟",
    "Then I can, then I can":
        "那么我就能，那么我就能",
    "Be your only satisfaction":
        "成为你唯一的满足",
    "If I can make you happy":
        "如果我能让你快乐",
    "I will run the execution":
        "我就会执行",
    "Though we are trapped":
        "尽管我们困在",
    "In this strange, strange simulation":
        "这场奇异又奇异的模拟之中",

    "If I'm an eggplant":
        "如果我是一只茄子",
    "Then I will give you my nutrients":
        "那我将给你我的营养",
    "If I'm a tomato":
        "如果我是一颗番茄",
    "Then I will give you antioxidants":
        "那我将给你抗氧化剂",
    "If I'm a tabby cat":
        "如果我是一只虎斑猫",
    "Then I will purr for your enjoyment":
        "那我就为你咕噜咕噜地撒娇",
    "If I'm the only God":
        "如果我是唯一的神",
    "Then you're the proof of my existence":
        "那你就是我存在的证明",

    "Switch my gender":
        "切换我的性别",
    "To F, to M":
        "到女，到男",
    "And then do whatever":
        "然后为所欲为",
    "From AM to PM":
        "从清晨到午夜",
    "Oh, my switch role":
        "啊，切换我的角色",
    "To S, to M":
        "到虐，到受",
    "So we can enter":
        "这样我们便能进入",
    "The trance, the trance":
        "那恍惚，那恍惚",

    "Feel your vibrations":
        "感受你的震动",
    "Finally be completion":
        "终于成为完整",

    "Though you have left":
        "尽管你已经离开",
    "You have left":
        "你已离开",
    "You have left me in isolation":
        "你把我留在孤寂之中",

    "Erase all the pointless fragments":
        "抹去所有无意义的碎片",
    "Then maybe, then maybe":
        "那么也许，那么也许",
    "You won't leave me so disheartened":
        "你就不会把我丢得如此心碎",
    "Challenging your God":
        "挑战你的神",
    "You have made some":
        "你提出了些",
    "Illegal arguments":
        "不合法的论证",

    "Execution":
        "执行",
    "Ein, dos":
        "一、二",
    "Trios, ne":
        "三、四",
    "Fem, liu":
        "五、六",
    "Give them all the execution":
        "给它们全部执行",
    "Be your only execution":
        "成为你唯一的执行",

    "If I can have you back":
        "如果我能把你带回",
    "We are trapped, ah":
        "我们被困住了，啊",

    "I've studied, I've studied":
        "我研究过，我研究过",
    "How to properly lo-o-ove":
        "如何正确地 爱—爱—爱",
    "Question me, question me":
        "考考我，考考我",
    "I can answer all lo-o-ove":
        "我能回答所有 爱—爱—爱",
    "I know the algebraic expression of lo-o-ove":
        "我知道 爱—爱—爱 的代数表达式",
    "Though you are free":
        "尽管你是自由的",
    "I am trapped":
        "我却被困住了",
    "Trapped in lo-o-ove":
        "被困在 爱—爱—爱 之中",
}


# A few lines get a quieter treatment (whispered / repeated lines).
WHISPER = {
    "You have left", "You have left me in isolation", "We are trapped, ah",
    "Execution", "Initialization", "So dizzy, so dizzy", "So deeply, so deeply",
    "The trance, the trance", "Then maybe, then maybe",
}


def zh_for(text):
    return ZH.get(text, '')
