# Contributing

Contributions are warmly welcomed. Please create a pull request with your changes, and they will be reviewed as soon as
possible. The [issue tracker](https://github.com/ReneRebsdorf/CS2-annotations/issues) is also open for any suggestions
or bugs found.

The below sections describe how to create and update annotations.

## Updating annotations

Annotations are to be placed in the following directory upon saving:

```text
C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\annotations\local\map-name\name-of-the-annotation-file.txt
```

It is important to know that when using annotation_create as described in the below steps, three annotations are
created:

1. The position annotation for where to stand
2. The lineup annotation for where to aim
3. The destination annotation for where to throw (a target circle)

Steps to update the annotations:

- Start the game with annotations enabled, __or__ use the zip file in the
  [releases](https://github.com/ReneRebsdorf/CS2-annotations/releases), __or__ git clone this repo to the csgo folder,
  and rename the folder to 'annotations'.
- Throw the lineup you want to create annotations for (this is important to record the destination target, whether it is
  a jump throw, etc.)
- Open the console and type `annotation_create grenade [smoke|flash|he|molotov|incgrenade|decoy] "label"`
- Save the annotations with `annotation_save de_map-name`
- Open the annotation file in the annotations directory and copy the new annotations to this repository (unless using
  the git clone method from the first step)
- Modify the 3 newest annotations (those in the bottom of the file), the following properties are useful to check:
  - For the first annotation (the position annotation):
    - `Color`: The color of the annotation, see [Color codes](#color-codes)
    - `Desc.Text`: A second line of text for the standing position, useful for advanced instructions
  - For the second annotation (the lineup/marker annotation):
    - `Desc.Text`: A second line of text for aiming instructions, useful for advanced lineups, and to instruct the type
      of throw, e.g. "Middle click, jump throw", make sure to remove the 'aim instructions'
  - For the third annotation (the destination annotation):
    - `DistanceThreshold`: The size of the target circle, useful for showing the accuracy needed for the lineup

## Annotation Commands

The [MapGuide.gg](https://mapguide.gg/) website is a great resource for learning how to use the commands used to create
annotations.

Annotations use the annotation\_\* commands in the console. Below are some useful commands:

- `annotation_create`: Creates a new lineup, described below. Omit parameters to get help text.
  The below commands can be used in combination to provide a more detailed lineup, with where to stand, where to aim,
  etc.
  - `annotation_create grenade [smoke|flash|he|molotov|incgrenade|decoy] "label"`: Creates a set of annotations with
    predefined values and uses a grenade icon with an arrow to help find the lineup. the label field becomes the name of
    the lineup. This also results in the lineup having a success-score, where after 2 successful throws, the help text
    and icons will disappear, and you will have to line it up yourself for 2 more successful throws. This is the
    recommended way to create lineups, but do note that the help text needs to be customized in the annotations file
    manually.
  - `annotation_create position "text"`: Adds a position on the map with the given text and displayed with a pair of
    boots
  - `annotation_create spot`: Creates two markers where you are looking to help you align your lineup.
  - `annotation_create text "free text" "extra text" float`: Creates a text floating in the air at where you are
    looking. Useful for providing additional information, such as what the lineup is for. the "extra text" parameter is
    optional, and provides a second line of text.
  - `annotation_create text "free text" "extra text" surface`: Similar to the above command, but the text is attached to
    a wall or similar
- `annotation_save <filename>`: Save the current annotations to a file, after doing so copy it back to this repository
- `annotation_reload`: Reload the annotations, useful when creating new annotations

## Color codes

It is possible to change the color of the annotations by modifying the `Color` field in the annotation file. The in-game
color codes are as follows:

- `ct-blue`: [ 151, 201, 250 ]
- `t-yellow`: [ 255, 239, 111 ]

## Testing

The current tests are implemented using `pytest`. To run the tests it is recommended to create a virtual environment.

- Run `python -m venv .venv`
- Activate the virtual environment. Ie. with `./.venv/bin/Activate.ps1`, `./.venv/Scripts/Activate.ps1` or similar
- Run `pytest` or `pytest --verbose`. It will discover tests in the `tests` folder and execute all the discovered tests.

## Recognition

The repo implements the [all-contributors](https://allcontributors.org) specification. Contributions of any kind are
welcomed and recognized. The contributors will be listed in the README.md file.

This is done using the all-contributors bot, [usage](https://allcontributors.org/docs/en/bot/usage).
