import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Dict, Tuple, Optional, List

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


themes = open_themes_desc(Path("data/puzzle_desc.xml"))
puzzles = open_puzzles(Path("data/lichess_db_puzzle.csv"))

L = []

for diff in range(1000, 3000, 500):
    p = puzzles[puzzles["Rating"] <= diff].sample(100000)
    diff_L = []
    for tag, theme in themes.items():
        pt = p[p["Themes"].str.contains(tag)]

        if len(pt):
            pt = pt.sample(min(len(pt), 100)).to_dict("records")
            diff_L.append((theme.name, "puzzles", pt, theme.desc))

    L.append((f"{diff} rated problems.", "list", diff_L, ""))

print(mk_book_from_list(L, level=0, book=True))

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Generate latex with chess puzzles from the lichess database"
    )

    parser.add_argument(
        "file",
        type=Path,
        help="Path to the .csv problem database. (Lichess problem format)",
    )
    parser.add_argument(
        "-t", "--theme", nargs="+", type=str, help="Name of the themes to be used."
    )
    parser.add_argument(
        "-m", "--min-rating", type=int, help="Minimum rating of the problems."
    )
    parser.add_argument(
        "-M", "--max-rating", type=int, help="Minimum rating of the problems."
    )
