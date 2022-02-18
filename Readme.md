## Pgn2Latex (WIP)

A simple script to make pdf from pgn files and studies. It's still work in progress and I hope to improve it in the future. Please feel to reach out or to contribute by submitting issues and pull requests!

### Examples

Some examples can be found in the `examples/` directory. At the moment there is a [book on the Stafford Gambit](https://github.com/icannos/pgn2tex/blob/master/examples/stafford.pdf) based on this [study](https://lichess.org/study/c9YhCd5b) and a [book of puzzles](https://github.com/icannos/pgn2tex/blob/master/examples/puzzles.pdf).

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

You first need to download the lichess puzzle database and the themes description, assuming you are in the root directory of the repo:

```
mkdir -p data 
cd data 
wget https://database.lichess.org/lichess_db_puzzle.csv.bz2 && bzip2 -d lichess_db_puzzle.csv.bz2 
wget https://raw.githubusercontent.com/lichess-org/lila/master/translation/source/puzzleTheme.xml
cd ..
```
Usage:
```
usage: puzzles.py [-h] [--problems PROBLEMS]
                  [--theme {advancedPawn,advantage,anastasiaMate,arabianMate,attackingF2F7,attraction,backRankMate,bishopEndgame,bodenMate,castling,capturingDefender,crushing,doubleBishopMate,dovetailMate,equality,kingsideAttack,clearance,defensiveMove,deflection,discoveredAttack,doubleCheck,endgame,exposedKing,fork,hangingPiece,hookMate,interference,intermezzo,knightEndgame,long,master,masterVsMaster,mate,mateIn1,mateIn2,mateIn3,mateIn4,mateIn5,middlegame,oneMove,opening,pawnEndgame,pin,promotion,queenEndgame,queenRookEndgame,queensideAttack,quietMove,rookEndgame,sacrifice,short,skewer,smotheredMate,superGM,trappedPiece,underPromotion,veryLong,xRayAttack,zugzwang,healthyMix,playerGames,puzzleDownloadInformation} [{advancedPawn,advantage,anastasiaMate,arabianMate,attackingF2F7,attraction,backRankMate,bishopEndgame,bodenMate,castling,capturingDefender,crushing,doubleBishopMate,dovetailMate,equality,kingsideAttack,clearance,defensiveMove,deflection,discoveredAttack,doubleCheck,endgame,exposedKing,fork,hangingPiece,hookMate,interference,intermezzo,knightEndgame,long,master,masterVsMaster,mate,mateIn1,mateIn2,mateIn3,mateIn4,mateIn5,middlegame,oneMove,opening,pawnEndgame,pin,promotion,queenEndgame,queenRookEndgame,queensideAttack,quietMove,rookEndgame,sacrifice,short,skewer,smotheredMate,superGM,trappedPiece,underPromotion,veryLong,xRayAttack,zugzwang,healthyMix,playerGames,puzzleDownloadInformation} ...]]
                  [-m MIN_RATING] [-s STEP_SIZE] [-M MAX_RATING] [--template TEMPLATE] [--front-page FRONT_PAGE] [--output OUTPUT]

Generate latex with chess puzzles from the lichess database

options:
  -h, --help            show this help message and exit
  --problems PROBLEMS, -p PROBLEMS
                        Max number of problems to sample in each theme/rating range.
  --theme {advancedPawn,advantage,anastasiaMate,arabianMate,attackingF2F7,attraction,backRankMate,bishopEndgame,bodenMate,castling,capturingDefender,crushing,doubleBishopMate,dovetailMate,equality,kingsideAttack,clearance,defensiveMove,deflection,discoveredAttack,doubleCheck,endgame,exposedKing,fork,hangingPiece,hookMate,interference,intermezzo,knightEndgame,long,master,masterVsMaster,mate,mateIn1,mateIn2,mateIn3,mateIn4,mateIn5,middlegame,oneMove,opening,pawnEndgame,pin,promotion,queenEndgame,queenRookEndgame,queensideAttack,quietMove,rookEndgame,sacrifice,short,skewer,smotheredMate,superGM,trappedPiece,underPromotion,veryLong,xRayAttack,zugzwang,healthyMix,playerGames,puzzleDownloadInformation} [{advancedPawn,advantage,anastasiaMate,arabianMate,attackingF2F7,attraction,backRankMate,bishopEndgame,bodenMate,castling,capturingDefender,crushing,doubleBishopMate,dovetailMate,equality,kingsideAttack,clearance,defensiveMove,deflection,discoveredAttack,doubleCheck,endgame,exposedKing,fork,hangingPiece,hookMate,interference,intermezzo,knightEndgame,long,master,masterVsMaster,mate,mateIn1,mateIn2,mateIn3,mateIn4,mateIn5,middlegame,oneMove,opening,pawnEndgame,pin,promotion,queenEndgame,queenRookEndgame,queensideAttack,quietMove,rookEndgame,sacrifice,short,skewer,smotheredMate,superGM,trappedPiece,underPromotion,veryLong,xRayAttack,zugzwang,healthyMix,playerGames,puzzleDownloadInformation} ...]
                        Name of the themes to be used.
  -m MIN_RATING, --min-rating MIN_RATING
                        Minimum rating of the problems.
  -s STEP_SIZE, --step-size STEP_SIZE
                        Step size from problem ratings
  -M MAX_RATING, --max-rating MAX_RATING
                        Maximum rating of the problems.
  --template TEMPLATE, -t TEMPLATE
                        Template file to use, if none only the latex content is generated with headers / document class, it can be input later on in any latex document.
  --front-page FRONT_PAGE, -f FRONT_PAGE
                        Path to a pdf frontpage
  --output OUTPUT, -o OUTPUT
                        Output file

```


Example:

```
python pgn2tex/puzzles.py --template pgn2tex/templates/book.tex --front-page pgn2tex/templates/frontpage_puzzles.pdf  --output examples/puzzles.tex
cd examples
xelatex puzzles.tex
xelatex puzzles.tex # for table of contents
```


### Code formatting 

The code is formatted using [Black](https://github.com/psf/black)
