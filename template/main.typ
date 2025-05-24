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

#show heading.where(level: 1): it => {
  set text(weight: "regular")
  smallcaps(it.body)
}

#show heading.where(level: 2): it => {
  set text(size: 3em, font: "FangSong")
  stack(dir: ttb, spacing: 0.5em, ..it.body.text.split(""))
}

#show heading.where(level: 3): it => box(height: 20%, width: 100%,
  align(horizon,
    text(weight: "bold", size: 1.5em, it.body)
  )
)

#show heading.where(level: 4): it => align(center,
  text(weight: "bold", size: 1.2em, it.body)
)

#show regex("<.+?>"): none

// functions for render
#let desc(content) = {
  if content != "" {
    box(width: 100%, inset: 2em,
      {
        set par(spacing: 1em, leading: 1em)
        h(2em)
        text(font: "FangSong", content)
      }
    )
  }
}

// property map
#let entry_type = (
  ACTIVITY_STORY: "SideStory",
  MAIN_STORY: "MainLine",
  MINI_STORY: "MiniStory",
  NONE: "OperatorRecords",
)

// data
#let entries = json("data.json")
#let side_stories = ()
#let main_stories = ()
#let mini_stories = ()
#let other_stories = ()
#for entry in entries {
  if entry.activity_type == "ACTIVITY_STORY" {
    side_stories.push(entry)
  }
  else if entry.activity_type == "MAIN_STORY" {
    main_stories.push(entry)
  }
  else if entry.activity_type == "MINI_STORY" {
    mini_stories.push(entry)
  }
  else if entry.activity_type == "NONE" {
    other_stories.push(entry)
  }
}

#let show_entries(entries) = {
  for entry in entries {
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
      // entry outline
      box(width: 50%, height: 90%,
        align(bottom, {
          context {
            set text(size: 1em)

            let last_name = ""
            for story in entry.stories {
              if last_name == "" or story.name != last_name {
                last_name = story.name

                let target = query(
                  heading.where(level: 3,
                  body: [#story.name])
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
          }
        })
      )
    )

    pagebreak()

    // content
    let last_name = ""
    for story in entry.stories {
      let new_story = last_name == "" or story.name != last_name
      set page(header: {
        set text(fill: luma(50%))
        box(width: 1fr, align(left, entry.name))
        box(width: 1fr, align(center)[泰拉观者])
        box(width: 1fr, align(right, story.code))
      })

      if new_story {
        last_name = story.name
        heading(level: 3, story.name)
        desc(story.description)
      }
      heading(level: 4, story.avg_tag)

      for line in story.texts {
        par(hanging-indent: name_width + name_spacing, {
          box(width: name_width, align(right, text(weight: "bold", line.name)))
          h(name_spacing)
          line.text
        })
      }

      if new_story {
        pagebreak()
      }
    }
  }
}

#let entries_outline(entries) = {
  context {
    for entry in entries {
      let target = query(
        heading.where(level: 2,
        body: [#entry.name])
      ).at(0)
      let location = target.location()
      let number = numbering(
        "1",
        ..counter(page).at(location),
      )
      link(location, stack(dir: ltr,
        box(width: 12em, target.body),
        h(1fr),
        box(width: 2em, number),
      ))
    }
  }
}

#heading(outlined: false, "泰拉观者")
#pagebreak()
#outline(title: "", target: heading.where(level: 1))
#pagebreak()

= MainLine
#entries_outline(main_stories)
#pagebreak()
#show_entries(main_stories)

= SideStory
#entries_outline(side_stories)
#pagebreak()
#show_entries(side_stories)

= MiniStory
#entries_outline(mini_stories)
#pagebreak()
#show_entries(mini_stories)

= OperatorRecords
#entries_outline(other_stories)
#pagebreak()
#show_entries(other_stories)
