from typing import Tuple, Dict, Iterator, List, Optional
import chess
import chess.pgn
import chess.svg
import uuid
import copy
from string import Template
import os
import argparse
from pathlib import Path

from utils import load_pgn, get_section_from_level


class PgnBook:
    """
    Class to represent a book parsed from a PGN file.
    """

    def __init__(self, path: Path, book=True, players=False) -> None:
        """
        path: path to the pgn file.
        book: wether or not we should use a latex book class or an article class
        """
        self.path = path
        self.book = book

        self.add_players = players

        self.count = 1

    def mk_chapter(self, game: chess.pgn.Game) -> str:
        """
        Build a chapter or a first level section. Called for each game
        of the pgn file. It starts the walk through the game and its
        variations
        """
        latex = ""
        title = game.headers["Event"]

        # Get the latex code for the section title
        latex += get_section_from_level(title, level=0, book=self.book) + "\n"

        # Used to add the QR code that point to the website where the game
        # can be found in an online analysis tool. Usually lichess
        latex += "\\thispagestyle{fancy} \n"
        latex += "\\rhead{"
        latex += "\\qrcode{" + game.headers["Site"] + "} } \n \n"

        # When exporting a game instead of a "study"
        if self.add_players:
            latex += "\\begin{center} \n"
            latex += "\\begin{tabular}{C{0.5\\textwidth}  C{0.5\\textwidth}} \n"
            latex += "\\includegraphics[width=0.2\\textwidth]{img/white_knight_logo.png} &  \\includegraphics[width=0.2\\textwidth]{img/black_knight_logo.png} \\\\ \n"

            latex += f"{game.headers['White']} & {game.headers['Black']} \\\\ \n"

            latex += f"{game.headers['WhiteElo']} & {game.headers['BlackElo']} \\\\ \n"
            # team

            if "WhiteTeam" in game.headers and "BlackTeam" in game.headers:
                latex += (
                    f"{game.headers['WhiteTeam']} & {game.headers['BlackTeam']} \\\\ \n"
                )

            latex += "\\end{tabular} \n"
            latex += "\\end{center} \n \n"

        # Initializes the board. It's used to record the moves
        # and generate san notation of the moves
        board = game.board()

        # Walk through the game
        latex += self.walk_game(board, game, level=0)

        return latex

    def walk_variation(
        self,
        current_var: List[chess.Move],
        board: chess.Board,
        node: chess.pgn.GameNode,
        start_var=False,
        first=False,
    ) -> str:
        """
        Function used to walk through variations (not the mainline). It supports
        infinitely nested subvariations and inside variations comments.

        current_var: list of moves currently stacked, waiting to be displayed
        board: current state of the board
        node: current game node
        start_var: if its the start of a new variation
        first: if it's the first step of the variation deviating from mainline
        """
        latex = ""

        current_var.append(node.move)

        # If we start a variation we add the starting comment to the text
        # if node.starts_variation:
        # latex += node.starting_comment + "\n \n"

        # node.variations contains the mainline at index 0,
        # If it has variations from here, ie more than 1 variation
        # We display the moves we have stacked until now
        # And we start a bullet point list, one entry per possible variations
        # from here
        if len(node.variations) > 1:
            board_save = copy.deepcopy(board)
            latex += "\\variation{" + board.variation_san(current_var) + "} \n"

            if not first:
                latex += node.comment + "\n"
            for mv in current_var:
                board_save.push(mv)
            latex += "\\begin{variants} \n"
            # If we are the first deviation, we exclude the mainline since it's
            # Already taken care of in the mainline
            if not first:
                latex += (
                    "\\item " + self.walk_variation([], board_save, node.next()) + "\n"
                )
            # Add an entry per possible variations
            for v in node.variations[1:]:
                latex += "\\item " + self.walk_variation([], board_save, v)
            latex += "\\end{variants} \n"
        # If there is a comment here, we flush the moves stacked untile now
        # we add the comment in the middle of the variation and then continue
        elif node.comment and not first:
            board_save = copy.deepcopy(board)
            latex += "\\variation{" + board.variation_san(current_var) + "} \n"
            node.set_arrows([])
            node.set_eval(score=None)
            latex += node.comment + "\n"
            for mv in current_var:
                board_save.push(mv)
            next_node = node.next()
            if next_node:
                latex += self.walk_variation([], board_save, next_node)

        # If there are no comments or different variations we just stack
        # one more move if there is one, or flush the moves if we reached the
        # end of the variation
        else:
            if not first:
                next_node = node.next()
                if next_node is not None:
                    latex += self.walk_variation(current_var, board, next_node)
                else:
                    latex += "\\variation{" + board.variation_san(current_var) + "} \n"
            else:
                return ""

        return latex

    def walk_game(self, board: chess.Board, game: chess.pgn.GameNode, level=0):
        """
        Go throug the mainline of a game and run walk_variation when necessary.
        Displays boards and comments only when necessary ie when there is a comment
        arrows on the board or different variations.
        Otherwise stacks the moves to be displayed at once next time it's required
        """
        latex = ""
        to_push = []

        # Uniq id used to identify a game in the latex code
        # Probably not the best way to do it but still good enough
        game_id = str(uuid.uuid4())

        # Get arrows/circles from the comment and remove it so we
        # can display the comments without these.
        arrows = game.arrows()
        game.set_arrows([])
        game.set_eval(score=None)

        # First add the comment for the whole game as introduction

        latex += game.comment + "\n \n"

        # We use a long table to make two columns one with the boards and the
        # other with the comments
        latex += "\\begin{longtable}{p{0.5\\textwidth} | p{0.5\\textwidth}} \n"

        # New game with xskak
        latex += "\\newchessgame[id=" + game_id + ","
        # Setup board from initial fen
        latex += (
            "setfen="
            + board.fen()
            + f", player={'w' if board.turn == chess.WHITE else 'b'},"
        )
        latex += "]\n"

        # Now we iterate over the mainline
        for node in game.mainline():
            # Stack move
            to_push.append(node.move)
            # If we want to display something
            node.set_eval(score=None)
            if node.comment or (len(node.variations) > 1) or node.is_end():
                latex += "\\mainline{" + board.variation_san(to_push) + "} \n \n"
                arrows = node.arrows()
                node.set_arrows([])
                for m in to_push:
                    board.push(m)

                # Display the board
                latex += "\\chessboard[lastmoveid =" + game_id + ","
                latex += "setfen=\\xskakgetgame{lastfen},"

                # Display circles and arrows
                for a in arrows:
                    if a.tail != a.head:
                        continue
                    latex += f"pgfstyle=border, color={a.color},"
                    latex += "markfield={" + chess.square_name(a.head) + "},"

                for a in arrows:
                    if a.tail == a.head:
                        continue

                    latex += f"pgfstyle=straightmove, color={a.color},"
                    latex += f"markmove={chess.square_name(a.tail)}-{chess.square_name(a.head)},"

                # Highlight last move
                latex += "pgfstyle=color, color=red!50, colorbackfields={\\xskakget{moveto}, \\xskakget{movefrom}},"

                latex += "]"

                # Add comment on the right column
                latex += " & " + node.comment + "\n \n"

                # We make a copy of the board not to perturb recursive calls
                boardt = copy.deepcopy(board)
                # We remove the last move: walk_variation begins at the very
                # name node we are in now
                boardt.pop()
                # Add variation in the right column
                latex += self.walk_variation(
                    [], boardt, node, start_var=True, first=True
                )
                latex += " \\\\ \n"

                to_push = []

        latex += "\\end{longtable} \n"

        return latex

    def latex(self) -> str:
        latex = ""
        self.count = 0
        for game in load_pgn(self.path):
            latex += self.mk_chapter(game)
            latex += "\n"
            self.count += 1
        return latex

    def singles(self) -> List[str]:
        result = []
        for game in load_pgn(self.path):
            result.append(self.mk_chapter(game))

        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a PGN file to a latex document. It is supposed to be used to create book from a study or a single game analysis."
    )

    parser.add_argument("file", type=Path, help="PGN File to parse")
    parser.add_argument(
        "--mode",
        "-m",
        choices=["single", "study"],
        default="single",
        help="Wether to treat each game independently or as one single large study with several chapters.",
    )
    parser.add_argument(
        "--players", "-p", action="store_true", help="Add player names", default=False
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

    parser.add_argument("-o", "--output", type=Path, default="output.tex")

    args = parser.parse_args()

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

    # Single game
    # uses a latex article class and section for each game
    if args.mode == "single":
        book = PgnBook(args.file, book=False, players=args.players)

        with open(args.output, "w") as fd:
            fd.write(
                template.substitute(frontpage=frontpage, content=book.singles()[0])
            )

    # When exporting a whole study it uses a book class and a chapter for each game
    elif args.mode == "study":
        book = PgnBook(args.file, book=True, players=args.players)

        with open(args.output, "w") as fd:
            fd.write(template.substitute(frontpage=frontpage, content=book.latex()))
    if args.mode == "study":
        book = PgnBook(args.file, book=True)
        with open(args.output, "w") as fd:
            fd.write(template.substitute(frontpage=frontpage, content=book.latex()))
