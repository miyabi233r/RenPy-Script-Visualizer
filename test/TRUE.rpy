label chapter_1:
    # 场景：一中校门口
    scene road with fade
    show bg_grain
    play music "audio/qianjin.ogg" fadein 1.0

    menu:
        "看到颜叙" if False: 
         
            jump yan_1

        "看到韩朔":
            $ han_favor += 1
            jump han_1

    "一中的校门在身后缓缓合上。\n三月就已透出初夏的燥热，空气微微扭曲。"
    
    # 场景切换
    scene classroom with dissolve
    show bg_grain
    play music "audio/wenhe.ogg" fadein 1.0

    desk "Hi，你就是新来的吧？\n我叫苏樱，是你的同桌。"
    "她抱着一大摞书重重放在我桌上，笑得眼睛弯弯。""\n除了开学典礼和年级大会，谁见过他亲自下楼接人啊？"
    stop music fadeout 1.0
    
    "下课铃响，同学们三三两两抱团走去食堂，转眼偌大的教室就空了下来。我走出门口，意外看到了颜叙站在那。"
    yan "你第一次来一中，走，我带你去食堂。"

    # 显示「次日」大字，2秒后自动消失
    scene black with dissolve
    show text "{font=ZCOOLXiaoWei-Regular.ttf}{size=60}第一天 完{/size}{/font}" at truecenter with dissolve

    # 2秒后自动隐藏
    $ renpy.pause(2.0, hard=True)
    hide text with dissolve

    play music "audio/morning.mp3" fadein 1.0
    
    "阳光从宿舍窗帘的缝隙透进来，落下几道光斑。"
    "走出宿舍楼，校园里已经有了不少学生，早晨的空气还带着一丝清凉。"
    #\n我下意识地往教学楼方向看了一眼，又迅速移开视线。
    scene road with dissolve
    show bg_grain
    
    "刚踏入教学楼一楼，我的目光被一个熟悉的身影吸引——颜叙正和几个学生会成员交代工作。\n他今天依旧穿着整齐的校服，领口扣得严严实实，声音冷静平稳。"
    
    "我本想低头绕过去，他却在一众嘈杂的人声中，精准地捕捉到了我的视线，对我微微颔首。"
    with Pause(0.5)
    yan "司徒望。"
    
    jump chapter_2
    jump chapter_3

 label yan_1:
    return


 label han_1:
    return

 label chapter_2:
    return

 label chapter_3:
    return