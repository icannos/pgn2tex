## Pgn2Latex (WIP)

A simple script to make pdf from pgn files and studies. It's still work in progress and I hope to improve it in the future. Please feel to reach out or to contribute by submitting issues and pull requests!

### Examples

Some examples can be found in the `examples/` directory. At the moment there is a [book on the Stafford Gambit](https://github.com/icannos/pgn2tex/blob/master/examples/stafford.pdf) based on this [study](https://lichess.org/study/c9YhCd5b).

### Requirements

#### Python

```
pip install -r requirements.txt
```

#### Latex 

It uses [xskak](https://www.ctan.org/pkg/xskak) and [skak](https://www.ctan.org/pkg/skak) to draw the chessboards. The latex files should be compiled using xelatex.

### Usage

#### Studies 
```
> python pgn2tex/study.py --help
usage: study.py [-h] [--mode {single,study}] [--players] [--template TEMPLATE] [--front-page FRONT_PAGE] [-o OUTPUT] file

Convert a PGN file to a latex document. It is supposed to be used to create book from a study or a single game analysis.

positional arguments:
  file                  PGN File to parse

options:
  -h, --help            show this help message and exit
  --mode {single,study}, -m {single,study}
                        Wether to treat each game independently or as one single large study with several chapters.
  --players, -p         Add player names
  --template TEMPLATE, -t TEMPLATE
                        Template file to use, if none only the latex content is generated with headers / document class, it can be input later on in any latex document.
  --front-page FRONT_PAGE, -f FRONT_PAGE
                        Path to a pdf frontpage
  -o OUTPUT, --output OUTPUT
```

```
> python pgn2tex/study.py examples/lichess_study_stafford-gambit_by_wyggam_2020.10.04.pgn --mode study -o examples/stafford.tex --template pgn2tex/templates/book.tex --front-page pgn2tex/templates/frontpage_stafford.pdf
> cd examples
> xelatex stafford.tex
> xelatex stafford.tex # for table of content and cross refs
```


#### Puzzles

WIP

### Code formatting 

The code is formatted using [Black](https://github.com/psf/black)
