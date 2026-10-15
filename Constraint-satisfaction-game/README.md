# Knight's Tour

An interactive Knight's Tour puzzle built with Python and pygame. Place a knight anywhere on the board and visit **every square exactly once** using only knight moves.

**Play it in your browser:** [Click here to play](https://knights-tour-five.vercel.app/)

<img width="500" height="350" alt="screenshot" src="https://github.com/user-attachments/assets/b9026401-bfca-425a-9e00-67cfb983e32c" />

## Features

- Four board sizes: 5x5, 6x6, 7x7 and 8x8
- Glowing dots show every legal move from the knight's square
- **Hint** suggests a move that can still finish the tour
- **Auto** lets the solver finish the tour for you, step by step
- **Undo** and **Restart**
- Optional path trail, step numbers and move counts (the number of onward moves from each square)
- Dead-end detection, a win celebration, and a special message for a *closed* tour that returns to the start square
- Animated welcome screen, smooth knight animations, and keyboard shortcuts

## How to play

1. Click any square to place your knight.
2. Click a glowing dot to jump there.
3. Keep going until all squares are visited. If you get stuck, use **Undo** or ask for a **Hint**.

Tip: turn on **Move counts**. A gold dot marks the move with the fewest onward options, which is usually the safest jump (the idea behind Warnsdorff's rule).

### Controls

| Key | Action |
|-----|--------|
| Click | Place the knight, then move |
| `H` | Hint |
| `A` | Auto-solve |
| `U` | Undo |
| `R` | Restart |
| `5` `6` `7` `8` or `S` | Change board size |
| `P` | Toggle path trail |
| `N` | Toggle step numbers |
| `D` | Toggle move counts |

## How it works

The tour is treated as a **constraint satisfaction problem (CSP)**:

- **Variables:** one per step, meaning which square the knight visits at that step
- **Domain:** all squares on the board
- **Constraints:** consecutive squares must be a knight's move apart, and no square may repeat

The solver behind **Hint** and **Auto** uses **backtracking search** with two improvements:

- **Forward checking:** reject a move that would leave an unvisited square with no way to continue
- **Fewest-onward-moves ordering** (the MRV heuristic, also known as Warnsdorff's rule): try the most constrained squares first

A node limit stops the solver from running too long. If no tour is found within the limit, the game tells you so and suggests using Undo.

## Run it on your computer

You need Python 3.9 or newer.

```bash
git clone https://github.com/spaul-tech/mini-projects.git
cd Constraint-satisfaction-game
pip install -r requirements.txt
python main.py
```

## Web version

The browser version is built with [pygbag](https://pypi.org/project/pygbag/), which compiles pygame games to WebAssembly. The ready-to-host files are in the [`web/`](web/) folder and can be deployed to any static host (Vercel, GitHub Pages, Netlify).

To rebuild after changing `main.py`:

```bash
pip install pygbag
python -m pygbag --build .
```

The build is written to `build/web`. Note that a rebuild overwrites `index.html` with the default loading page. The custom loading page is kept in `web/index.html`, so copy it back over the generated one before deploying.

## Project structure

```
knights-tour/
├── main.py            # the whole game (CSP solver, UI, animations)
├── requirements.txt   # pygame
├── web/               # ready-to-deploy browser build
│   ├── index.html     # custom loading page
│   ├── knights_tour.apk
│   ├── knights_tour.tar.gz
│   └── favicon.png
└── README.md
```

## Tech

Python, pygame, pygbag (WebAssembly)

## License

Add a license if you want others to reuse the code, for example [MIT](https://choosealicense.com/licenses/mit/).
