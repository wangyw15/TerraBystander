// config
#let nickname = "博士"
#let data_path = "data.json"
#let skin_path = ""

// read from input
#{
  if "nickname" in sys.inputs {
    nickname = sys.inputs.nickname
  }
  if "data" in sys.inputs {
    data_path = sys.inputs.data
  }
  if "skin" in sys.inputs {
    skin_path = sys.inputs.skin
  }
}

// layout and style
#let name_width = 8em
#let name_spacing = 1em
#set page(
  "a5",
  numbering: "1",
  margin: (x: 1.75cm, y: 2.75cm),
)

#set text(
  font: (
    (name: "Times New Roman", covers: "latin-in-cjk"),
    "Source Han Serif SC"
  ),
  lang: "zh",
  region: "cn",
  weight: "regular",
  size: 10.5pt,
)

#set par(justify: true, spacing: 1.3em, leading: 1.3em)

#show heading.where(level: 1): it => {
  set text(weight: "regular")
  smallcaps(it.body)
}

#let vertical_text(t) = {
  if t == none {
    return
  }
  block(rotate(90deg, reflow: true, {
    let chars = t.split("")
    chars.remove(0)
    chars.remove(-1)

    let elements = ()
    let en_regex = regex("[A-Za-z0-9,.:;]")
    for c in chars {
      if c == "" {
        continue
      }
      if c.match(en_regex) == none {
        box(width: 0.3em)
        box({
          rotate(-90deg, origin: horizon + center, reflow: true, c)
        })
      }
      else {
        c
      }
    }
  }))
}

#show heading.where(level: 2): it => {
  set text(size: 2.5em, font: "FangSong")
  vertical_text(it.body.text)
}

#show heading.where(level: 3): it => block(height: 20%, width: 100%,
  align(horizon,
    text(weight: "bold", size: 1.5em, it.body)
  )
)

#show heading.where(level: 4): it => align(center,
  text(weight: "bold", size: 1.2em, it.body)
)

// #show regex("<.+?>"): none
#let color_regex = regex("<color=#(\S+?)>(.*?)</color>")
#show color_regex: it => {
  let (c, t) = it.text.match(color_regex).captures
  text(fill: rgb(c), t)
}

#let nickname_regex = regex("\{\@[Nn]ickname\}")
#show nickname_regex: text(nickname)

// property map
#let entry_type = (
  ACTIVITY_STORY: "SideStory",
  MAIN_STORY: "MainLine",
  MINI_STORY: "MiniStory",
  NONE: "OperatorRecords",
)

// data
#let data = json(data_path)
#let side_stories = ()
#let main_stories = ()
#let mini_stories = ()
#for activity in data.activities {
  if activity.activity_type == "ACTIVITY_STORY" {
    side_stories.push(activity)
  }
  else if activity.activity_type == "MAIN_STORY" {
    main_stories.push(activity)
  }
  else if activity.activity_type == "MINI_STORY" {
    mini_stories.push(activity)
  }
}

// functions for render
#let description(content) = {
  if content != "" {
    block(width: 100%, inset: 2em,
      {
        set par(spacing: 1em, leading: 1em)
        h(2em)
        text(font: "FangSong", content)
      }
    )
  }
}

#let sub_heading(content) = {
  rotate(90deg, origin: top + start, reflow: true, {
    set text(size: 2em)
    h(2.5em)
    smallcaps(content)
  })
}

#let narrator(body) = {
  let replaced = body.replace(nickname_regex, nickname)
  for char in replaced.split("") {
    box(skew(ax: -15deg, text(fill: luma(40%), weight: "semibold", char)))
  }
}

#let show_avg_story(story, show_title: true, show_description: true, show_avg_tag: true) = {
  if show_title {
    heading(level: 3, story.name)
  }
  if show_description {
    description(story.description)
  }

  if show_avg_tag {
    heading(level: 4, story.avg_tag)
  }

  for line in story.texts {
    if line.name == "" {
      par(first-line-indent: name_width + name_spacing,
          hanging-indent: name_width + name_spacing - 2em,
          narrator(line.text)
      )
    }
    else {
      par(hanging-indent: name_width + name_spacing, {
        box(width: name_width, align(right, text(weight: "bold", line.name)))
        h(name_spacing)
        line.text
      })
    }
  }
}

#let default_outline_line(target, page_number) = {
    stack(dir: ltr,
      box(width: 12em, target.body),
      h(1fr),
      box(width: 3em, align(right, page_number)),
    )
  }

#let custom_outline(target_selector, custom_line: default_outline_line) = {
  context {
    let query_result = query(target_selector)
    if query_result.len() > 0 {
      let target = query_result.at(0)
      let location = target.location()
      let number = numbering(
        "1",
        ..counter(page).at(location),
      )
      link(location, custom_line(target, number))
    }
  }
}

#let show_activities(activities) = {
  for activity in activities {
    stack(
      dir: ltr,
      h(1em),
      sub_heading(activity.secondary_name),
      h(1em),
      heading(level: 2, activity.name),
      h(1fr),
      {
        // activity type
        align(top + right, {
          set text(size: 3em)
          smallcaps(entry_type.at(activity.activity_type))
        })
      
        // activity outline
        align(right + bottom,
          context {
            set text(size: 1em)

            let last_name = ""
            for story in activity.stories {
              if last_name == "" or story.name != last_name {
                last_name = story.name

                let custom_line(target, number) = {
                  block(stack(dir: ltr,
                    box(width: 5em, align(right, story.code)),
                    h(1em),
                    box(width: 10em, align(left, target.body)),
                    h(1em),
                    box(width: 2em, align(right, number)),
                  ))
                }
                custom_outline(
                  heading.where(level: 3, body: [#story.name]),
                  custom_line: custom_line,
                )
              }
            }
          }
        )
      }
    )

    pagebreak()

    // content
    let last_name = ""
    for story in activity.stories {
      let new_story = last_name == "" or story.name != last_name
      last_name = story.name

      set page(header: {
        set text(fill: luma(50%))
        box(width: 1fr, align(left, activity.name))
        box(width: 1fr, align(center)[泰拉观者])
        box(width: 1fr, align(right, story.code))
      })

      show_avg_story(story, show_title: new_story, show_description: new_story, show_avg_tag: true)

      // below is useless because the page is set above
      if new_story {
        pagebreak()
      }
    }
  }
}

#let volume_outline(activities) = context {
  for activity in activities {
    custom_outline(
      heading.where(level: 2, body: [#activity.name]),
    )
  }
}

#heading(outlined: false, "泰拉观者")

文件生成日期：#datetime.today().display()

游戏数据版本：#data.metadata.version

游戏数据日期：#data.metadata.date.split("/").join("-")

#pagebreak()
#outline(title: "", target: heading.where(level: 1))
#pagebreak()

= MainLine
#volume_outline(main_stories)
#pagebreak()
#show_activities(main_stories)

= SideStory
#volume_outline(side_stories)
#pagebreak()
#show_activities(side_stories)

= MiniStory
#volume_outline(mini_stories)
#pagebreak()
#show_activities(mini_stories)

= Operator
#volume_outline(data.operators)
#pagebreak()

#{
  // show heading.where(level: 2): it => {
  //   text(size: 2.5em, font: "FangSong", it.body.text)
  // }
  for operator in data.operators {
    set page(header: {
      set text(fill: luma(50%))
      box(width: 1fr, align(left, operator.appellation))
      box(width: 1fr, align(center)[泰拉观者])
      box(width: 1fr, align(right, operator.name))
    })

    if skin_path != "" {
      set align(center + bottom)
      block(height: 1fr,
        figure(
          image(
            fit: "contain",
            skin_path + "/" + operator.id + "_1b.png"
          )
        )
      )
    }
    {
      show text: it => box({
        text(stroke: white + 1.5pt, it)
        place(top + start, text(it))
      })

      place(right + top, stack(dir: rtl, spacing: 1em, 
        heading(level: 2, operator.name),
        sub_heading(operator.appellation),
      ))
      place(left + top, stack(dir: ltr, spacing: 1em,
        vertical_text(operator.usage),
        vertical_text(operator.description),
        {
          v(0.3em)
          vertical_text(operator.profession)
          vertical_text(operator.sub_profession)
        },
      ))
    }

    pagebreak()

    if operator.operator_stories.len() > 0 {
      set page(header: {
        set text(fill: luma(50%))
        box(width: 1fr, align(left)[干员档案])
        box(width: 1fr, align(center)[泰拉观者])
        box(width: 1fr, align(right, operator.name))
      })

      heading(level: 3)[干员档案]

      for story in operator.operator_stories {
        heading(level: 4, story.title)

        for line in story.text.split("\n") {
          par(first-line-indent: 2em, line.trim())
        }
      }
      pagebreak()
    }

    if operator.voices.len() > 0 {
      set page(header: {
        set text(fill: luma(50%))
        box(width: 1fr, align(left)[语音记录])
        box(width: 1fr, align(center)[泰拉观者])
        box(width: 1fr, align(right, operator.name))
      })

      heading(level: 3)[语音记录]

      for voice in operator.voices {
        heading(level: 4, voice.title)
        par(first-line-indent: 2em, voice.text)
      }
      pagebreak()
    }

    if operator.avgs.len() > 0 {
      set page(header: {
        set text(fill: luma(50%))
        box(width: 1fr, align(left)[干员密录])
        box(width: 1fr, align(center)[泰拉观者])
        box(width: 1fr, align(right, operator.name))
      })

      heading(level: 3)[干员密录]
      // outline
      for activity in operator.avgs {
        custom_outline(
          heading.where(level: 4, body: [#activity.name])
        )
      }
      pagebreak()

      // content
      let showed_name = false
      for activity in operator.avgs {
        for story in activity.stories {
          set page(header: {
            set text(fill: luma(50%))
            box(width: 1fr, align(left, activity.name))
            box(width: 1fr, align(center)[泰拉观者])
            box(width: 1fr, align(right, operator.name))
          })

          if not showed_name {
            heading(level: 4, activity.name)
            showed_name = true
          }
          show_avg_story(story, show_title: false, show_avg_tag: false)
        }
      }
      pagebreak()
    }
  }
}

#pagebreak()

项目地址：#link("https://github.com/wangyw15/TerraBystander")[https://github.com/wangyw15/TerraBystander]

封面/协助：#link("https://space.bilibili.com/148232872")[君曜\@Bilbili https://space.bilibili.com/148232872]

版权归属：鹰角网络

试读致谢：Wojuray，白河
