import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Dict, Tuple, Optional, List
from string import Template
import os

import chess.pgn
import chess
import chess.svg

from tqdm import tqdm
from argparse import ArgumentParser, HelpFormatter

from dataclasses import dataclass

from utils import load_pgn, get_section_from_level


@dataclass
class PuzzleTheme:
    id: str
    name: str
    desc: str


def open_puzzles(path: Path):
    puzzles = pd.read_csv(
        path,
        names=[
            "PuzzleId",
            "FEN",
            "Moves",
            "Rating",
            "RatingDeviation",
            "Popularity",
            "NbPlays",
            "Themes",
            "GameUrl",
        ],
    )
    return puzzles


def open_themes_desc(path: Path) -> Dict[str, PuzzleTheme]:
    tree = ET.parse(path)

    themes = {}
    for child in tree.getroot():
        name = child.attrib["name"]
        d = len("Description")
        if name[-d:] != "Description":
            themes[name] = PuzzleTheme(id=name, name=child.text, desc="")
        else:
            if name[:-d] in themes:
                themes[name[:-d]].desc = child.text
    return themes


def turn2str(turn):
    if turn == chess.WHITE:
        return "White"
    else:
        return "Black"


def mk_latex_puzzle(puzzle):
    board = chess.Board(fen=puzzle["FEN"])

    moves = puzzle["Moves"].split(" ")
    moves = [chess.Move.from_uci(move) for move in moves]
    board.push(moves[0])

    latex = "\\newgame \n"
    latex += "\n"
    latex += "\\fenboard{" + board.fen() + "}"
    latex += "\n"
    latex += "\n \n"
    latex += "\\showboard"
    latex += "\n \n "
    latex += f"{turn2str(board.turn)} to move. \n \n"
    latex += "Solution: \\mainline{" + board.variation_san(moves[1:]) + "}"
    latex += "\n \n"

    return latex


def mk_book_from_list(L, level=0, book=True) -> str:
    latex = ""
    for l in L:
        if l[1] == "puzzles":
            latex += "\\newpage \n"
            latex += get_section_from_level(l[0], level, book)
            latex += "\n"
            latex += l[3]
            latex += "\\begin{multicols}{2} \n"
            for p in l[2]:
                latex += "\\begin{samepage} \n"
                latex += mk_latex_puzzle(p)
                latex += "\\end{samepage}"
            latex += "\\end{multicols} \n"
        else:
            latex += get_section_from_level(l[0], level, book)
            latex += "\n"
            latex += l[3]
            latex += mk_book_from_list(l[2], level=level + 1, book=book)

    return latex


themes = open_themes_desc(Path("data/puzzleTheme.xml"))

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Generate latex with chess puzzles from the lichess database"
    )

    parser.add_argument(
        "--problems",
        "-p",
        type=int,
        default=5,
        help="Max number of problems to sample in each theme/rating range.",
    )
    parser.add_argument(
        "--theme",
        nargs="+",
        type=str,
        help="Name of the themes to be used.",
        choices=[tag for tag, _ in themes.items()],
    )
    parser.add_argument(
        "-m",
        "--min-rating",
        type=int,
        help="Minimum rating of the problems.",
        default=1000,
    )
    parser.add_argument(
        "-s",
        "--step-size",
        type=int,
        help="Step size from problem ratings",
        default=500,
    )
    parser.add_argument(
        "-M",
        "--max-rating",
        type=int,
        help="Maximum rating of the problems.",
        default=2500,
    )
    parser.add_argument(
        "--template",
        "-t",
        type=Path,
        help="Template file to use, if none only the latex content is generated with headers / document class, it can be input later on in any latex document.",
        default=None,
    )

    parser.add_argument(
        "--front-page", "-f", help="Path to a pdf frontpage", default=None
    )

    parser.add_argument("--output", "-o", type=Path, help="Output file", default=None)

    args = parser.parse_args()

    puzzles = open_puzzles(Path("data/lichess_db_puzzle.csv"))

    L = []

    for diff in range(args.min_rating, args.max_rating, args.step_size):
        p = puzzles[puzzles["Rating"] <= diff]

        if len(p) < 10000:
            p = p.sample(len(p))
        else:
            p = p.sample(
                10000
            )  # We take a subsample of the puzzles so the filtering is not too slow
        diff_L = []
        for tag, theme in themes.items():
            if args.theme is not None and tag not in args.theme:
                continue

            pt = p[p["Themes"].str.contains(tag)]

            if len(pt):
                pt = pt.sample(min(len(pt), args.problems)).to_dict("records")
                diff_L.append((theme.name, "puzzles", pt, theme.desc))

        L.append((f"{diff} rated problems.", "list", diff_L, ""))

    content = mk_book_from_list(L, level=0, book=True)

    if args.template is None:
        template = "$content"
    else:
        with args.template.open("r") as f:
            template = f.read()

    template = Template(template)

    frontpage = (
        ("\\includepdf[pages=1, noautoscale]{%s}" % os.path.abspath(args.front_page))
        if args.front_page
        else ""
    )
    with open(args.output, "w") as fd:
        fd.write(template.substitute(frontpage=frontpage, content=content))
