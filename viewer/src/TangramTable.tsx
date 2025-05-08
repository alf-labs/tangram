import {type ReactElement, useEffect, useState} from "react";
import Table from 'react-bootstrap/Table';
import BoardImage from "./BoardImage.tsx";

interface TableData {
    index: number;
    perm: number;
    found: boolean;
    pieces: string;
    board: string;
    boardLines: string[];
}

function TangramTable() : ReactElement {
    const [tableData, setTableData] = useState<TableData[]>([]);
    const [status, setStatus] = useState("Loading...");

    useEffect(() => {
        fetchData()
    }, []);

    function stringifyError(error: unknown) {
        if (error instanceof Error) {
            return error.message;
        } else {
            return String(error);
        }
    }

    const lineLengths = [7, 9, 11, 11, 9, 7];
    function splitBoard(board:string): string[] {
        const lines : string[] = [];
        let start = 0;
        for (const len of lineLengths) {
            const end = start + len;
            lines.push(board.substring(start, end));
            start = end;
        }
        return lines;
    }

    async function fetchData() {
        try {
            const response = await fetch("/data.txt");
            if (!response.ok) {
                throw new Error(`Error reading data: ${response.status}`);
            }
            const content = await response.text();
            const tableData: TableData[] = [];

            const piecesDuplicates = new Set<string>();

            setStatus("Parsing...");
            const pattern = /^@@\s+\[(\d+)]\s+SIG\s+(\S+)\s+(.+)$/;
            for (const line of content.split("\n")) {
                const matches = line.trim().match(pattern);
                if (matches) {
                    const pieces = matches[3].replace(/,/g, " ");
                    if (!piecesDuplicates.has(pieces)) {
                        const entry: TableData = {
                            index: 0,
                            perm: parseInt(matches[1], 10),
                            found: false,
                            board: matches[2],
                            boardLines: splitBoard(matches[2]),
                            pieces: pieces,
                        }
                        piecesDuplicates.add(pieces);
                        tableData.push(entry);
                    }
                }
            }

            // Sort the array first by "perm" (ascending) and then by "pieces" (ascending)
            tableData.sort((a, b) => {
                // First comparison: by "perm"
                if (a.perm !== b.perm) {
                    return a.perm - b.perm;
                }

                // If "perm" is the same, then compare by "pieces"
                if (a.pieces < b.pieces) {
                    return -1;
                } else  if (a.pieces > b.pieces) {
                    return 1;
                }
                return 0; // all the same
            });

            // Compute the index after sorting
            let index: number = 1;
            for  (const entry of tableData) {
                entry.index = index++;
            }

            setTableData(tableData);
            setStatus(`${tableData.length} entries loaded.`);
        } catch (err) {
            setStatus(stringifyError(err));
        }
    }

    return (
    <>
        <div>{status}</div>
        <Table striped bordered hover>
            <thead>
            <tr>
                <th>#</th>
                <th>Perm</th>
                <th>Found</th>
                <th>Pieces</th>
                <th>Board</th>
                <th>Board</th>
            </tr>
            </thead>
            <tbody>
            {
                tableData.map((item:TableData) =>
                    <tr key={item.index}>
                    <td id="r{item.index}"><a href="#r{item.index}">{item.index}</a></td>
                    <td>{item.perm}</td>
                    <td>{item.found ? "Yes" : "--"}</td>
                    <td>{item.pieces}</td>
                    <td className="board text-center">
                        {
                            item.boardLines.map((line) => (
                                <span key={`${item.index}-${line}"`}>{line}</span>
                            ))
                        }
                    </td>
                    <td>
                        <BoardImage board={item.board} />
                    </td>
                    </tr>
                )
            }
            </tbody>
        </Table>
    </>
    )
}

export default TangramTable
