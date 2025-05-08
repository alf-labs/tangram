import {type ReactElement, useEffect, useRef} from "react";

// Let's call X'Y' the pixel coordinate system.
// The board uses an "YRG" coordinate system:
// "R" is oriented like X', straight horizontal towards increasing X'.
// "Y" is a "slanted" version of Y', at a 120 angle instead of 90, towards increasing Y'.
// Each YR combo forms a rhombus, which is split in 2 parts: g=0 (higher Y') vs g=1 (lower Y').

const VALID_YRG = [
    [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1], [0, 3, 0],
    [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1], [1, 3, 0], [1, 3, 1], [1, 4, 0],
    [2, 0, 0], [2, 0, 1], [2, 1, 0], [2, 1, 1], [2, 2, 0], [2, 2, 1], [2, 3, 0], [2, 3, 1], [2, 4, 0], [2, 4, 1], [2, 5, 0],
    [3, 0, 1], [3, 1, 0], [3, 1, 1], [3, 2, 0], [3, 2, 1], [3, 3, 0], [3, 3, 1], [3, 4, 0], [3, 4, 1], [3, 5, 0], [3, 5, 1],
    [4, 1, 1], [4, 2, 0], [4, 2, 1], [4, 3, 0], [4, 3, 1], [4, 4, 0], [4, 4, 1], [4, 5, 0], [4, 5, 1],
    [5, 2, 1], [5, 3, 0], [5, 3, 1], [5, 4, 0], [5, 4, 1], [5, 5, 0], [5, 5, 1],
];

type StringToStringMap = { [key: string]: string };
const COLORS : StringToStringMap = {
    "Y": "#DDA044",
    "R": "#CC0000",
    "O": "#EE6600",
    "B": "#808080",
    "W": "#EEDDCC",
    "U": "#00FF00",  // unknown color
}

const STROKE_COLOR = "#404040";

const boardSize = 6;
const boardImgWidth = 120;
const cachedBoardCells: BoardCellPoints[] = [];


interface BoardImageProps {
    board: string;
}

interface BoardCellPoints {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    x3: number;
    y3: number;
}

function BoardImage(props: BoardImageProps) : ReactElement {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        canvas.width = boardImgWidth;
        canvas.height = computeHeight(boardImgWidth);

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        if (cachedBoardCells.length === 0) {
            computeBoardCells(canvas.width, canvas.height);
        }

        let index = 0;
        const letters = props.board;
        for (let cell of cachedBoardCells) {
            const letter = letters.slice(index, ++index);
            const color = COLORS[letter] || COLORS["U"];
            drawCell(ctx, cell, color);
        }
    }, [props.board]);

    function computeHeight(width: number): number {
        // Height = Width * sin(60 degrees). pi/3=60 degrees.
        return Math.ceil(width * Math.sin(Math.PI / 3));
    }

    function computeBoardCells(width: number, height: number) {
        const cx = width / 2;
        const cy = height / 2;
        const radius = width / 2;
        const N2 = boardSize / 2;

        // Compute the YRG Y and R vectors. pi/3*2=120 degrees.
        const rx = radius / N2;
        const ry = 0;
        const yx = rx * Math.cos(Math.PI / 3 * 2);
        const yy = rx * Math.sin(Math.PI / 3 * 2);

        function pointYR(y:number, r: number): number[] {
            const px = cx + r * rx + y * yx;
            const py = cy + r * ry + y * yy;
            return [ px, py ];
        }

        for (let yrg of VALID_YRG) {
            const y= yrg[0] - N2;
            const r= yrg[1] - N2;
            const g= yrg[2];
            const p0 = pointYR(y    , r)
            const p1 = pointYR(y + 1, r)
            const p2 = pointYR(y + 1, r + 1)
            const p3 = pointYR(y    , r + 1)
            if (g == 0) {
                const triangle : BoardCellPoints = {
                    x1: p0[0], y1: p0[1],
                    x2: p1[0], y2: p1[1],
                    x3: p2[0], y3: p2[1],
                }
                cachedBoardCells.push(triangle);
            } else {
                const triangle : BoardCellPoints = {
                    x1: p0[0], y1: p0[1],
                    x2: p2[0], y2: p2[1],
                    x3: p3[0], y3: p3[1],
                }
                cachedBoardCells.push(triangle);
            }
        }
    }

    function drawCell(ctx: CanvasRenderingContext2D, cell: BoardCellPoints, color: string) {
        ctx.beginPath();
        ctx.moveTo(cell.x1, cell.y1);
        ctx.lineTo(cell.x2, cell.y2);
        ctx.lineTo(cell.x3, cell.y3);
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = STROKE_COLOR;
        ctx.stroke();
    }

    return <canvas ref={canvasRef} />;
}

export default BoardImage
