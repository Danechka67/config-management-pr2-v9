"""Представления графа Mermaid, ASCII и PNG."""

from collections import deque
import json
from math import atan2, cos, pi, sin

NODE_HEIGHT = 34
ROW = 80
GAP = 30
MARGIN = 25
ARROW = 10
FONT = 15
MAX_PIXELS = 30_000_000


def mermaid(graph):
    """Записать все вершины и рёбра с безопасными идентификаторами."""
    ids = {node: f"n{index}" for index, node in enumerate(graph)}
    lines = ["flowchart TD"]
    for node, ident in ids.items():
        label = node.replace("&", "&amp;").replace('"', "&quot;")
        lines.append(f"    {ident}[{json.dumps(label, ensure_ascii=False)}]")
    for node, targets in graph.items():
        lines.extend(f"    {ids[node]} --> {ids[child]}" for child in targets)
    return "\n".join(lines) + "\n"


def tree(graph, root):
    """Показать повторные ссылки без повторного раскрытия ветвей."""
    seen, stack, lines = set(), [(root, "", "", "")], []
    while stack:
        node, prefix, marker, padding = stack.pop()
        duplicate = node in seen
        ending = " [уже показан]" if duplicate else ""
        lines.append(f"{prefix}{marker}{node}{ending}")
        if duplicate:
            continue
        seen.add(node)
        children = graph[node]
        entries = [(child, prefix + padding, "|-- ", "|   ")
                   for child in children[:-1]]
        if children:
            entries.append((children[-1], prefix + padding, "`-- ", "    "))
        stack.extend(reversed(entries))
    return "\n".join(lines)


def layers(graph, root):
    """Разбить вершины на уровни по расстоянию от корня."""
    result, seen, queue = [], {root}, deque([(root, 0)])
    while queue:
        node, level = queue.popleft()
        if level == len(result):
            result.append([])
        result[level].append(node)
        for child in graph[node]:
            if child not in seen:
                seen.add(child)
                queue.append((child, level + 1))
    return result


def positions(rows, width, cell):
    """Расположить вершины каждого уровня по центру изображения."""
    return {
        node: ((width - len(nodes) * cell) // 2 + index * cell + cell // 2,
               MARGIN + level * ROW + NODE_HEIGHT // 2)
        for level, nodes in enumerate(rows)
        for index, node in enumerate(nodes)
    }


def arrow(draw, points):
    """Нарисовать ломаное ребро со стрелкой."""
    draw.line(points, fill="#506983", width=2)
    (before_x, before_y), (end_x, end_y) = points[-2:]
    angle = atan2(end_y - before_y, end_x - before_x)
    tip = [(end_x, end_y)]
    for shift in (-pi / 6, pi / 6):
        tip.append((end_x - ARROW * cos(angle + shift),
                    end_y - ARROW * sin(angle + shift)))
    draw.polygon(tip, fill="#506983")


def edge(draw, source, target, half_width):
    """Вывести стрелку на границу карточки, включая петли и обратные рёбра."""
    x, y = source
    tx, ty = target
    half = NODE_HEIGHT // 2
    if source == target:
        side = x + half_width
        arrow(draw, [(side, y - 6), (side + 12, y - 6),
                     (side + 12, y + 6), (side, y + 6)])
    elif ty == y:
        direction = 1 if tx > x else -1
        arrow(draw, [(x, y - half), (x, y - half - 10),
                     (tx - direction * 10, y - half - 10),
                     (tx - direction * 10, y - half)])
    elif ty > y:
        arrow(draw, [(x, y + half), (tx, ty - half)])
    else:
        arrow(draw, [(x + 8, y - half), (tx + 8, ty + half)])


def png(graph, root, path):
    """Сохранить PNG графа. Pillow используется только для рисования."""
    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.load_default(size=FONT)
    rows = layers(graph, root)
    card = int(max(font.getlength(node) for node in graph)) + GAP
    cell = card + GAP
    width = max(map(len, rows)) * cell + MARGIN * 2
    height = len(rows) * ROW + MARGIN
    if width * height > MAX_PIXELS:
        raise ValueError("граф слишком велик для PNG; задайте --filter")
    centers = positions(rows, width, cell)
    image = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(image)
    for node, targets in graph.items():
        for child in targets:
            edge(draw, centers[node], centers[child], card // 2)
    for node, (x, y) in centers.items():
        box = (x - card // 2, y - NODE_HEIGHT // 2,
               x + card // 2, y + NODE_HEIGHT // 2)
        fill = "#d7eaff" if node == root else "#ffffff"
        draw.rounded_rectangle(box, radius=7, fill=fill, outline="#3b6288")
        draw.text((x, y), node, font=font, anchor="mm", fill="#12263a")
    image.save(path, format="PNG")
