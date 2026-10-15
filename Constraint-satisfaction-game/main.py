"""Knight's Tour - upgraded edition (pygame).  pip install pygame

Visit every square exactly once using knight moves.

CSP view: one variable per step (which square), domain = squares, constraints =
consecutive squares are a knight move apart and every square is different.
The solver behind Hint / Auto uses backtracking with forward checking and the
fewest-onward-moves (Warnsdorff / MRV) ordering.

Controls
  Click            place the knight, then click a glowing dot to move
  H  Hint          a move that can still finish the tour
  A  Auto          watch the solver finish the tour
  U  Undo          R  Restart          5 6 7 8  or  S : board size
  P  path    N  numbers    D  move counts      Esc : quit
"""
import asyncio
import colorsys
import math
import random
import sys
import pygame

MOVES = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
SIZES = [5, 6, 7, 8]


def nbrs(N, p):
    r, c = p
    return [(r + dr, c + dc) for dr, dc in MOVES if 0 <= r + dr < N and 0 <= c + dc < N]


# ----------------------------------------------------------------- CSP part
class Timeout(Exception):
    pass


def solve(N, path, limit=40000):
    """Complete `path` into a full tour. Returns the remaining squares ([] if
    already complete) or None if no tour was found within the node budget."""
    visited = set(path)
    total = N * N
    out = []
    nodes = [0]

    def deg(p):
        return sum(1 for q in nbrs(N, p) if q not in visited)

    def rec(pos):
        if len(visited) == total:
            return True
        nodes[0] += 1
        if nodes[0] > limit:
            raise Timeout
        remaining = total - len(visited)
        cands = [m for m in nbrs(N, pos) if m not in visited]
        cands = [m for m in cands if deg(m) > 0 or remaining == 1]  # forward check
        cands.sort(key=deg)  # fewest onward moves first (MRV)
        for m in cands:
            visited.add(m)
            out.append(m)
            if rec(m):
                return True
            out.pop()
            visited.discard(m)
        return False

    try:
        return list(out) if rec(path[-1]) else None
    except Timeout:
        return None


# ----------------------------------------------------------------- helpers
W, H = 990, 720
FR_X, FR_Y, FR_SIZE, MARGIN = 36, 84, 600, 26
PX = FR_X + FR_SIZE + 36
PW = W - PX - 30

BG_TOP, BG_BOT = (30, 35, 56), (14, 16, 28)
LIGHT, DARK = (238, 217, 181), (174, 128, 93)
WOOD, WOOD_HI, WOOD_LO = (88, 60, 42), (128, 92, 64), (52, 34, 24)
WHITE, MUTED = (248, 249, 253), (150, 158, 184)
CARD = (38, 44, 68)
ACCENT, ACCENT_HI = (98, 132, 238), (128, 158, 255)
GREEN, GOLD, RED, ORANGE = (72, 196, 118), (255, 208, 80), (232, 82, 82), (255, 150, 70)
INK = (28, 32, 52)

_fonts = {}


def font(size, bold=True):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.Font(None, int(size * 1.3))
    return _fonts[key]


def txt(surf, s, size, color, pos, anchor="topleft", bold=True):
    img = font(size, bold).render(str(s), True, color)
    rect = img.get_rect()
    setattr(rect, anchor, pos)
    surf.blit(img, rect)
    return rect


def wrap(s, size, maxw, bold=False):
    lines, cur = [], ""
    for w in s.split():
        test = (cur + " " + w).strip()
        if font(size, bold).size(test)[0] > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    lines.append(cur)
    return lines


def mix(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def hsv(h, s=0.65, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def smooth(t):
    return t * t * (3 - 2 * t)


def rrect(surf, rect, color, radius=12, alpha=None, width=0):
    rect = pygame.Rect(rect)
    if alpha is None:
        pygame.draw.rect(surf, color, rect, width, border_radius=radius)
    else:
        layer = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(layer, tuple(color) + (alpha,), layer.get_rect(), width, border_radius=radius)
        surf.blit(layer, rect.topleft)


_sprites = {}


def knight_sprite(px, body, edge=(255, 255, 255)):
    """Anti-aliased knight silhouette, drawn large and scaled down."""
    key = (px, body, edge)
    if key in _sprites:
        return _sprites[key]
    big = 320
    s = pygame.Surface((big, big), pygame.SRCALPHA)
    pts = [(.22, .90), (.25, .72), (.33, .57), (.30, .47), (.19, .41), (.15, .32),
           (.25, .22), (.33, .10), (.38, .21), (.45, .07), (.50, .20), (.63, .26),
           (.75, .43), (.79, .64), (.77, .90)]
    P = [(x * big, y * big) for x, y in pts]
    pygame.draw.polygon(s, body, P)
    # mane highlight
    mane = [(.50, .20), (.63, .26), (.75, .43), (.79, .64), (.70, .50), (.60, .38), (.48, .30)]
    pygame.draw.polygon(s, mix(body, (255, 255, 255), 0.18), [(x * big, y * big) for x, y in mane])
    pygame.draw.polygon(s, edge, P, 9)
    # base
    base = pygame.Rect(.17 * big, .86 * big, .66 * big, .10 * big)
    pygame.draw.rect(s, body, base, border_radius=14)
    pygame.draw.rect(s, edge, base, 9, border_radius=14)
    # eye and nostril
    pygame.draw.circle(s, edge, (int(.36 * big), int(.30 * big)), 10)
    pygame.draw.circle(s, mix(body, edge, .5), (int(.19 * big), int(.37 * big)), 6)
    out = pygame.transform.smoothscale(s, (int(px), int(px)))
    _sprites[key] = out
    return out


class Button:
    def __init__(self, label, key, rect, action, enabled):
        self.label, self.key, self.rect = label, key, pygame.Rect(rect)
        self.action, self.enabled = action, enabled


class Confetti:
    def __init__(self):
        self.items = []

    def burst(self, n=150):
        for _ in range(n):
            self.items.append([random.uniform(FR_X + 80, FR_X + FR_SIZE - 80), FR_Y + 160,
                               random.uniform(-260, 260), random.uniform(-720, -220),
                               hsv(random.random(), .7, 1), random.randint(5, 10)])

    def update(self, dt):
        for p in self.items:
            p[3] += 1100 * dt
            p[0] += p[2] * dt
            p[1] += p[3] * dt
        self.items = [p for p in self.items if p[1] < H + 20]

    def draw(self, surf):
        for x, y, _, _, col, sz in self.items:
            pygame.draw.rect(surf, col, (int(x), int(y), sz, sz // 2 + 2), border_radius=2)


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Knight's Tour")
        self.clock = pygame.time.Clock()
        self.bg = self.make_background()
        self.confetti = Confetti()
        self.N = 6
        self.show_path, self.show_nums, self.show_counts = True, True, False
        self.cursor_hand = False
        self.hover = None
        self.mouse = (0, 0)
        self.intro_fade = 1.0
        self.build_buttons()
        self.reset()

    # ------------------------------------------------------------ state
    @property
    def S(self):
        return (FR_SIZE - 2 * MARGIN) // self.N

    @property
    def ox(self):
        return FR_X + (FR_SIZE - self.N * self.S) // 2

    @property
    def oy(self):
        return FR_Y + (FR_SIZE - self.N * self.S) // 2

    def reset(self, keep_msg=False):
        self.path = []
        self.hint = None
        self.queue = []
        self.anim = None
        self.last_step = 0
        self.start_ok = None
        self.shake_t0 = -10_000
        self.win_t0 = None
        self.intro_fade = 1.0
        self.confetti.items.clear()
        if not keep_msg:
            self.say("Click any square to place your knight.", "info")

    def say(self, text, kind="info"):
        self.msg, self.msg_kind = text, kind

    def set_size(self, n):
        if n != self.N:
            self.N = n
            self.reset()

    def deg(self, p):
        v = set(self.path)
        return sum(1 for q in nbrs(self.N, p) if q not in v)

    def legal(self):
        if not self.path:
            return []
        v = set(self.path)
        return [m for m in nbrs(self.N, self.path[-1]) if m not in v]

    def done(self):
        return len(self.path) == self.N * self.N

    def stuck(self):
        return bool(self.path) and not self.done() and not self.legal()

    def closed(self):
        return self.done() and self.path[0] in nbrs(self.N, self.path[-1])

    # ------------------------------------------------------------ actions
    def knight_xy(self):
        """Current drawn position (row, col as floats) and hop height 0..1."""
        if self.anim:
            (fr, fc), (tr, tc), t0, dur, kind = self.anim
            t = (pygame.time.get_ticks() - t0) / dur
            if t >= 1:
                self.anim = None
            else:
                e = smooth(t) if kind == "hop" else 1 - (1 - t) ** 3
                hop = math.sin(math.pi * t) if kind == "hop" else 0.0
                return (fr + (tr - fr) * e, fc + (tc - fc) * e), hop
        return (float(self.path[-1][0]), float(self.path[-1][1])), 0.0

    def start_anim(self, frm, to, kind="hop", dur=300):
        self.anim = (frm, to, pygame.time.get_ticks(), dur, kind)

    def place(self, p, fast=False):
        self.hint = None
        if not self.path:
            self.path.append(p)
            self.start_ok = solve(self.N, self.path) is not None
            self.start_anim((p[0] - 1.6, p[1]), p, "drop", 380)
            if self.start_ok:
                self.say("Nice start. Click a glowing dot to jump.", "info")
            else:
                self.say("Careful: no full tour was found from this square. "
                         "You can still explore, or restart and pick another.", "warn")
            return
        if p not in self.legal():
            return
        cur, _ = self.knight_xy()
        self.path.append(p)
        self.start_anim(cur, p, "hop", 150 if fast else 300)
        n, total = len(self.path), self.N ** 2
        if self.done():
            self.win_t0 = pygame.time.get_ticks()
            self.confetti.burst(180)
            self.say("Closed tour! It even returns to the start square."
                     if self.closed() else "Tour complete! Every square visited once.", "gold")
        elif self.stuck():
            self.shake_t0 = pygame.time.get_ticks()
            self.say("Dead end: no moves left. Undo a few moves, or press Hint.", "bad")
        else:
            self.say(f"{n} of {total} squares visited, {total - n} to go.", "info")

    def undo(self):
        if not self.path:
            return
        self.queue, self.hint = [], None
        self.win_t0 = None
        self.confetti.items.clear()
        cur, _ = self.knight_xy()
        if len(self.path) == 1:
            self.path.clear()
            self.anim = None
            self.say("Click any square to place your knight.", "info")
            return
        self.path.pop()
        self.start_anim(cur, self.path[-1], "hop", 220)
        self.say("Move undone.", "info")

    def do_hint(self):
        if not self.path or self.done():
            return
        self.queue = []
        rest = solve(self.N, self.path)
        if rest:
            self.hint = rest[0]
            self.say("Gold ring: a move that can still finish the tour.", "gold")
        else:
            self.hint = None
            self.say("No complete tour found from here. Try Undo.", "warn")

    def do_auto(self):
        if not self.path or self.done():
            return
        rest = solve(self.N, self.path)
        if rest is None:
            self.say("No complete tour found from here. Try Undo.", "warn")
        else:
            self.queue = rest
            self.hint = None
            self.say("Solver is finishing the tour. Click anywhere to stop.", "info")

    def toggle(self, name):
        setattr(self, name, not getattr(self, name))
        if name == "show_counts" and self.show_counts:
            self.say("Numbers show onward moves. Gold = fewest: usually the safest jump.", "info")

    # ------------------------------------------------------------ widgets
    def build_buttons(self):
        bw = (PW - 10) // 2
        y0 = 452
        spec = [("Hint", "H", self.do_hint, lambda: bool(self.path) and not self.done()),
                ("Auto", "A", self.do_auto, lambda: bool(self.path) and not self.done()),
                ("Undo", "U", self.undo, lambda: bool(self.path)),
                ("Restart", "R", lambda: self.reset(), lambda: bool(self.path))]
        self.buttons = []
        for i, (label, key, act, en) in enumerate(spec):
            rect = (PX + (i % 2) * (bw + 10), y0 + (i // 2) * 54, bw, 46)
            self.buttons.append(Button(label, key, rect, act, en))
        self.size_rects = [pygame.Rect(PX + i * (PW // 4), 268, PW // 4 - 6, 38) for i in range(4)]
        self.toggles = [("Path trail", "show_path", pygame.Rect(PX, 336, PW, 32)),
                        ("Step numbers", "show_nums", pygame.Rect(PX, 372, PW, 32)),
                        ("Move counts", "show_counts", pygame.Rect(PX, 408, PW, 32))]

    def make_background(self):
        bg = pygame.Surface((W, H))
        for y in range(H):
            pygame.draw.line(bg, mix(BG_TOP, BG_BOT, y / H), (0, y), (W, y))
        glow = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.circle(glow, (98, 132, 238, 26), (200, 150), 260)
        pygame.draw.circle(glow, (255, 150, 200, 16), (W - 120, H - 80), 300)
        bg.blit(glow, (0, 0))
        return bg

    def cell_at(self, pos):
        c, r = (pos[0] - self.ox) // self.S, (pos[1] - self.oy) // self.S
        if pos[0] >= self.ox and pos[1] >= self.oy and 0 <= r < self.N and 0 <= c < self.N:
            return (r, c)
        return None

    def centre(self, r, c):
        return (self.ox + (c + .5) * self.S, self.oy + (r + .5) * self.S)

    # ------------------------------------------------------------ events
    def click(self, pos):
        self.queue = []
        for b in self.buttons:
            if b.rect.collidepoint(pos):
                if b.enabled():
                    b.action()
                return
        for i, r in enumerate(self.size_rects):
            if r.collidepoint(pos):
                self.set_size(SIZES[i])
                return
        for _, name, r in self.toggles:
            if r.collidepoint(pos):
                self.toggle(name)
                return
        cell = self.cell_at(pos)
        if cell:
            self.place(cell)

    def key(self, k):
        names = {pygame.K_h: "Hint", pygame.K_a: "Auto", pygame.K_u: "Undo", pygame.K_r: "Restart"}
        if k in names:
            for b in self.buttons:
                if b.label == names[k] and b.enabled():
                    b.action()
        elif k == pygame.K_s:
            self.set_size(SIZES[(SIZES.index(self.N) + 1) % len(SIZES)])
        elif pygame.K_5 <= k <= pygame.K_8:
            self.set_size(k - pygame.K_0)
        elif k == pygame.K_p:
            self.toggle("show_path")
        elif k == pygame.K_n:
            self.toggle("show_nums")
        elif k == pygame.K_d:
            self.toggle("show_counts")

    def clickable_under_mouse(self):
        pos = self.mouse
        if any(b.rect.collidepoint(pos) and b.enabled() for b in self.buttons):
            return True
        if any(r.collidepoint(pos) for r in self.size_rects):
            return True
        if any(r.collidepoint(pos) for _, _, r in self.toggles):
            return True
        if self.hover:
            return (not self.path) or self.hover in self.legal()
        return False

    # ------------------------------------------------------------ update
    def update(self, dt):
        now = pygame.time.get_ticks()
        if self.queue and now - self.last_step > 170:
            self.place(self.queue.pop(0), fast=True)
            self.last_step = now
        self.confetti.update(dt)
        if self.win_t0 is not None and now - self.win_t0 < 2500 and random.random() < 0.1:
            self.confetti.burst(12)
        # welcome card fades out while the mouse is over the board so it never hides a square
        target = 0.1 if (self.hover and not self.path) else 1.0
        self.intro_fade += (target - self.intro_fade) * min(1.0, dt * 10)
        hand = self.clickable_under_mouse()
        if hand != self.cursor_hand:
            self.cursor_hand = hand
            try:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if hand else pygame.SYSTEM_CURSOR_ARROW)
            except Exception:
                pass

    # ------------------------------------------------------------ drawing
    def draw_start_overlay(self, surf, now):
        """Welcome screen shown before the knight is placed: a shimmering wave
        across the squares plus a glowing, animated 'Place your knight' card."""
        N, S, ox, oy = self.N, self.S, self.ox, self.oy
        side = N * S
        t = now / 1000.0
        pulse = 0.5 + 0.5 * math.sin(t * 3.0)

        # 1) diagonal shimmer sweeping over every square
        layer = pygame.Surface((side, side), pygame.SRCALPHA)
        for r in range(N):
            for c in range(N):
                wave = 0.5 + 0.5 * math.sin(t * 2.4 - (r + c) * 0.75)
                a = int(95 * wave ** 3)
                if a > 2:
                    pygame.draw.rect(layer, (255, 236, 150, a), (c * S, r * S, S, S))
        surf.blit(layer, (ox, oy))

        # 2) welcome card
        fade = self.intro_fade
        cw, ch = min(side - 40, 430), 262
        card = pygame.Rect(0, 0, cw, ch)
        card.center = (ox + side // 2, oy + side // 2)

        # soft pulsing glow behind the card
        for i, base in enumerate((46, 28, 14)):
            grow = 10 + i * 12 + int(8 * pulse)
            rrect(surf, card.inflate(grow, grow), GOLD, 34 + i * 6, alpha=int(base * fade))

        cs = pygame.Surface(card.size, pygame.SRCALPHA)
        pygame.draw.rect(cs, (20, 24, 44, 240), cs.get_rect(), border_radius=26)
        pygame.draw.rect(cs, mix(ACCENT_HI, GOLD, pulse) + (255,), cs.get_rect(), 3, border_radius=26)

        # bouncing knight with a breathing shadow
        bob = abs(math.sin(t * 3.0))
        shadow_w = 54 - 20 * bob
        pygame.draw.ellipse(cs, (0, 0, 0, int(110 - 50 * bob)),
                            (cw / 2 - shadow_w / 2, 112, shadow_w, 11))
        spr = knight_sprite(92, GOLD)
        cs.blit(spr, spr.get_rect(center=(cw // 2, 62 - int(bob * 16))))

        txt(cs, "Place your knight", 32, WHITE, (cw // 2, 142), "center")
        txt(cs, "Click any square to start your tour", 18, mix(MUTED, WHITE, 0.35 + 0.35 * pulse),
            (cw // 2, 178), "center", bold=False)

        chip_txt = f"Visit all {N * N} squares exactly once"
        chip_w = font(14).size(chip_txt)[0] + 32
        chip = pygame.Rect(0, 0, chip_w, 30)
        chip.center = (cw // 2, 218)
        pygame.draw.rect(cs, ACCENT + (255,), chip, border_radius=15)
        txt(cs, chip_txt, 14, WHITE, chip.center, "center")

        cs.set_alpha(int(255 * fade))
        surf.blit(cs, card.topleft)

    def draw_board(self, surf, now):
        N, S, ox, oy = self.N, self.S, self.ox, self.oy
        side = N * S
        frame = pygame.Rect(ox - MARGIN, oy - MARGIN, side + 2 * MARGIN, side + 2 * MARGIN)
        rrect(surf, frame.move(0, 10), (0, 0, 0), 22, alpha=90)
        rrect(surf, frame, WOOD, 22)
        rrect(surf, frame, WOOD_HI, 22, width=3)
        rrect(surf, frame.inflate(-10, -10), WOOD_LO, 18, width=2)

        total = N * N
        order = {p: i for i, p in enumerate(self.path)}
        last = self.path[-1] if self.path else None
        for r in range(N):
            for c in range(N):
                base = DARK if (r + c) % 2 else LIGHT
                if (r, c) in order:
                    base = mix(base, hsv(0.56 + 0.40 * order[(r, c)] / max(total - 1, 1), .7, 1), 0.42)
                if (r, c) == last:
                    base = mix(base, GOLD, 0.55)
                pygame.draw.rect(surf, base, (ox + c * S, oy + r * S, S, S))
        for i in range(N):
            txt(surf, "abcdefgh"[i], max(13, S // 5), (224, 196, 158),
                (ox + (i + .5) * S, oy + side + MARGIN // 2 + 1), "center")
            txt(surf, N - i, max(13, S // 5), (224, 196, 158),
                (ox - MARGIN // 2 - 1, oy + (i + .5) * S), "center")

        # trail
        if self.show_path and len(self.path) > 1:
            layer = pygame.Surface((W, H), pygame.SRCALPHA)
            pts = [self.centre(*p) for p in self.path]
            for i in range(len(pts) - 1):
                col = hsv(0.56 + 0.40 * i / max(total - 1, 1), .75, 1)
                pygame.draw.line(layer, col + (70,), pts[i], pts[i + 1], max(8, S // 5))
                pygame.draw.line(layer, col + (235,), pts[i], pts[i + 1], max(3, S // 18))
            if self.closed():
                pygame.draw.line(layer, GOLD + (255,), pts[-1], pts[0], max(4, S // 14))
            surf.blit(layer, (0, 0))

        # step nodes
        for i, p in enumerate(self.path):
            if p == last:
                continue
            x, y = self.centre(*p)
            col = hsv(0.56 + 0.40 * i / max(total - 1, 1), .75, .95)
            rad = max(5, int(S * 0.14))
            pygame.draw.circle(surf, WHITE, (int(x), int(y)), rad + 2)
            pygame.draw.circle(surf, col, (int(x), int(y)), rad)
            if self.show_nums:
                txt(surf, i + 1, max(10, int(S * 0.17)), INK, (x, y), "center")

        # legal moves
        legal = self.legal()
        if legal and not self.done():
            degs = {p: self.deg(p) for p in legal}
            lo = min(degs.values())
            pulse = 0.5 + 0.5 * math.sin(now / 280)
            for p in legal:
                x, y = self.centre(*p)
                col = GOLD if (self.show_counts and degs[p] == lo) else GREEN
                big = self.hover == p
                rad = S * (0.17 + 0.03 * pulse + (0.04 if big else 0))
                rrect(surf, (x - S * .32, y - S * .32, S * .64, S * .64), col, int(S * .32),
                      alpha=int(40 + 50 * pulse + (60 if big else 0)))
                pygame.draw.circle(surf, col, (int(x), int(y)), int(rad))
                pygame.draw.circle(surf, WHITE, (int(x), int(y)), int(rad), 2)
                if self.show_counts:
                    txt(surf, degs[p], max(12, int(S * 0.2)), INK, (x, y), "center")

        # hint
        if self.hint:
            x, y = self.centre(*self.hint)
            pulse = 0.5 + 0.5 * math.sin(now / 200)
            pygame.draw.circle(surf, GOLD, (int(x), int(y)), int(S * (0.36 + 0.06 * pulse)), 5)
            pygame.draw.circle(surf, WHITE, (int(x), int(y)), int(S * (0.36 + 0.06 * pulse)) + 5, 1)

        # welcome card (only before the knight is placed)
        if not self.path:
            self.draw_start_overlay(surf, now)

        # hover on empty board: ghost knight (drawn above the card)
        if not self.path and self.hover:
            x, y = self.centre(*self.hover)
            rrect(surf, (x - S / 2, y - S / 2, S, S), WHITE, 0, alpha=50)
            ghost = knight_sprite(S * 0.84, (40, 44, 70)).copy()
            ghost.set_alpha(150)
            surf.blit(ghost, ghost.get_rect(center=(x, y)))

        # dead-end flash
        since = now - self.shake_t0
        if 0 <= since < 600:
            flash = pygame.Surface((side, side), pygame.SRCALPHA)
            flash.fill(RED + (int(110 * (1 - since / 600)),))
            surf.blit(flash, (ox, oy))

    def draw_knight(self, surf, now):
        if not self.path:
            return
        S = self.S
        (r, c), hop = self.knight_xy()
        x, y = self.centre(r, c)
        since = now - self.shake_t0
        if 0 <= since < 600:
            x += math.sin(since / 22) * 7 * (1 - since / 600)
        body = (38, 42, 68)
        if self.done():
            body = (214, 160, 30)
        elif self.stuck():
            body = (170, 44, 44)
        # shadow
        sw = S * (0.52 - 0.18 * hop)
        shadow = pygame.Surface((int(S), int(S)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, int(95 - 40 * hop)),
                            (S / 2 - sw / 2, S * 0.74, sw, S * 0.16))
        surf.blit(shadow, (x - S / 2, y - S / 2))
        spr = knight_sprite(S * 0.84, body)
        surf.blit(spr, spr.get_rect(center=(x, y - hop * S * 0.38 - S * 0.02)))

    def draw_panel(self, surf, now):
        txt(surf, "Knight's Tour", 36, WHITE, (PX, 22))
        txt(surf, "Visit every square exactly once.", 15, MUTED, (PX, 66), bold=False)

        # stats card
        rrect(surf, (PX, 100, PW, 128), CARD, 16)
        n, total = len(self.path), self.N ** 2
        txt(surf, "SQUARES VISITED", 12, MUTED, (PX + 16, 114))
        txt(surf, n, 44, WHITE, (PX + 16, 130))
        w = font(44).size(str(n))[0]
        txt(surf, f"/ {total}", 22, MUTED, (PX + 22 + w, 156))
        bar = pygame.Rect(PX + 16, 196, PW - 32, 14)
        rrect(surf, bar, (24, 28, 46), 7)
        frac = n / total
        if frac > 0:
            fill = pygame.Rect(bar.x, bar.y, max(14, int(bar.w * frac)), bar.h)
            rrect(surf, fill, mix(ACCENT, GOLD, frac), 7)

        # board size
        txt(surf, "BOARD SIZE", 12, MUTED, (PX, 246))
        for i, r in enumerate(self.size_rects):
            sel = SIZES[i] == self.N
            hov = r.collidepoint(self.mouse)
            rrect(surf, r, ACCENT if sel else (ACCENT_HI if hov else CARD), 10)
            txt(surf, f"{SIZES[i]}x{SIZES[i]}", 16, WHITE if sel or hov else MUTED, r.center, "center")

        # toggles
        for label, name, r in self.toggles:
            on = getattr(self, name)
            txt(surf, label, 16, WHITE, (r.x + 2, r.centery), "midleft", bold=False)
            track = pygame.Rect(0, 0, 46, 24)
            track.midright = (r.right - 2, r.centery)
            rrect(surf, track, GREEN if on else (66, 72, 100), 12)
            kx = track.right - 13 if on else track.left + 13
            pygame.draw.circle(surf, WHITE, (kx, track.centery), 9)

        # buttons
        for b in self.buttons:
            en = b.enabled()
            hov = en and b.rect.collidepoint(self.mouse)
            col = (ACCENT_HI if hov else ACCENT) if en else (50, 55, 78)
            rrect(surf, b.rect.move(0, 3), (0, 0, 0), 12, alpha=70 if en else 0)
            rrect(surf, b.rect, col, 12)
            txt(surf, b.label, 18, WHITE if en else (110, 116, 140), (b.rect.centerx - 8, b.rect.centery), "center")
            txt(surf, b.key, 12, mix(col, WHITE, .6) if en else (90, 96, 120),
                (b.rect.right - 14, b.rect.centery), "center")

        # status card (pulses and uses larger text until the knight is placed)
        kinds = {"info": ACCENT, "good": GREEN, "warn": ORANGE, "bad": RED, "gold": GOLD}
        col = kinds[self.msg_kind]
        card = pygame.Rect(PX, 566, PW, 98)
        rrect(surf, card, CARD, 16)
        start = not self.path
        if start:
            pulse = 0.5 + 0.5 * math.sin(now / 260)
            col = mix(GOLD, WHITE, 0.4 * pulse)
            rrect(surf, card.inflate(4, 4), col, 18, width=3)
        rrect(surf, (card.x, card.y + 14, 6, card.h - 28), col, 3)
        size = 17 if start else 15
        y = card.y + 14
        for line in wrap(self.msg, size, PW - 48)[:4]:
            txt(surf, line, size, WHITE, (card.x + 22, y), bold=start)
            y += size + 5
        txt(surf, "H hint  A auto  U undo  R restart  S size", 12, MUTED, (PX, H - 40), bold=False)

    def draw(self):
        now = pygame.time.get_ticks()
        self.screen.blit(self.bg, (0, 0))
        txt(self.screen, "Tour the whole board", 18, MUTED, (FR_X + 4, 40), bold=False)
        self.draw_board(self.screen, now)
        self.draw_knight(self.screen, now)
        self.draw_panel(self.screen, now)
        self.confetti.draw(self.screen)
        pygame.display.flip()

    # ------------------------------------------------------------ main loop
    async def run(self):
        while True:
            dt = self.clock.tick(60) / 1000
            self.mouse = pygame.mouse.get_pos()
            self.hover = self.cell_at(self.mouse)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.click(e.pos)
                if e.type == pygame.KEYDOWN:
                    self.key(e.key)
            self.update(dt)
            self.draw()
            await asyncio.sleep(0)  # let the browser breathe


if __name__ == "__main__":
    asyncio.run(App().run())
