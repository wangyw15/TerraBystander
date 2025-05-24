// layout
#set page(numbering: "1", margin: (x: 2cm, y: 2cm))
#let name_width = 10em
#let name_spacing = 1.5em

// style
#set text(
  font: (
    (name: "Times New Roman", covers: "latin-in-cjk"),
    "Source Han Serif SC"
  ),
  lang: "zh",
  region: "cn",
  weight: "regular"
)

#set par(justify: true, spacing: 1.3em, leading: 1.3em)

#show heading.where(level: 2): it => {
  set text(size: 3em, font: "FangSong")
  stack(dir: ttb, spacing: 0.5em, ..it.body.text.split(""))
}

#show heading.where(level: 3): it => box(height: 20%, width: 100%,
  align(horizon,
    text(weight: "bold", size: 1.5em, it.body)
  )
)

// functions for render
#let desc(content) = {
  box(width: 100%, inset: 2em,
    {
      set par(spacing: 1em, leading: 1em)
      h(2em)
      text(font: "FangSong", content)
    }
  )
}

// data
// property map
#let entry_type = (
  ACTIVITY_STORY: "SideStory",
  MAIN_STORY: "MainLine",
  MINI_STORY: "MiniStory",
  NONE: "None",
)

// content
#{
  let data = json("data.json")
  for entry in data {
    // chapter cover
    align(right, {
      set text(size: 3em)
      smallcaps(entry_type.at(entry.activity_type))
    })

    stack(
      dir: ltr,
      h(1fr),
      heading(level: 2, entry.name),
      h(3fr),
       box(width: 50%, height: 90%,
         align(bottom, {
          context {
            set text(size: 1em)
            for story in entry.stories {
              let target = query(
                heading.where(level: 3,
                body: [#(story.name + "（" + story.avg_tag + "）")])
              ).at(0)
              let location = target.location()
              let number = numbering(
                "1",
                ..counter(page).at(location),
              )
              link(location, stack(dir: ltr,
                box(width: 5em, align(right, story.code)),
                h(1em),
                box(width: 12em, target.body),
                h(1fr),
                box(width: 2em, number),
              ))
            }
          }
        })
      )
    )

    pagebreak()

    // content
    for story in entry.stories {
      set page(header: {
        set text(fill: luma(50%))
        entry.name
        h(1fr)
        "泰拉观者"
        h(1fr)
        story.code
      })

      heading(level: 3, story.name + "（" + story.avg_tag + "）")
      desc(story.description)
      v(1em)

      for line in story.texts {
        par(hanging-indent: name_width + name_spacing, {
          box(width: name_width, align(right, text(weight: "bold", line.name)))
          h(name_spacing)
          line.text
        })
      }
      pagebreak()
    }
  }
}
