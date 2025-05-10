import {type ReactElement, useEffect, useState} from "react";
import Table from 'react-bootstrap/Table';
import {BoardImageInView} from "./BoardImage.tsx";

// Data URL is relative to the public/ folder (in npm dev) or index.html (in prod).
const GENERATOR_TXT_URL = "generator.txt"
const ANALYZER_JSON_URL = "analyzer.json"
const TANGRAM_RELATIVE_URL = "../tangram/";

interface TableData {
    index: number;
    perm: number;
    found_idx: number;
    found_href: string|null;
    pieces: string;
    board: string;
    boardLines: string[];
}

interface AnalyzerItem {
    href: string;
    index: number;
    sig: string
}

function TangramTable() : ReactElement {
    const [tableData, setTableData] = useState<TableData[]>([]);
    const [status, setStatus] = useState("Loading...");
    const [numMatches, setNumMatches] = useState(-1);

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

    const LINE_LENGTHS = [7, 9, 11, 11, 9, 7];
    function splitBoard(board:string): string[] {
        const lines : string[] = [];
        let start = 0;
        for (const len of LINE_LENGTHS) {
            const end = start + len;
            lines.push(board.substring(start, end));
            start = end;
        }
        return lines;
    }

    async function fetchData() {
        try {
            // Parse the analyzer data
            const analyzerData = await fetch(ANALYZER_JSON_URL);
            if (!analyzerData.ok) {
                throw new Error(`Error reading data: ${analyzerData.status}`);
            }
            const analyzerList = await analyzerData.json();
            const analyzerMap: Map<string, AnalyzerItem> = new Map();
            for (const item of analyzerList) {
                const a_item = item as AnalyzerItem;
                analyzerMap.set(a_item.sig, a_item);
            }

            // Parse the generator data
            const generatorData = await fetch(GENERATOR_TXT_URL);
            if (!generatorData.ok) {
                throw new Error(`Error reading data: ${generatorData.status}`);
            }
            const generatorContent = await generatorData.text();
            const tableData: TableData[] = [];

            const piecesDuplicates = new Set<string>();

            setStatus("Parsing...");
            const pattern = /^@@\s+\[(\d+)]\s+SIG\s+(\S+)\s+(.+)$/;
            let maxPerm = 0;
            let num_found = 0;
            for (const line of generatorContent.split("\n")) {
                const matches = line.trim().match(pattern);
                if (matches) {
                    const pieces = sortPieces(matches[3].split(",")).join(" ");
                    if (!piecesDuplicates.has(pieces)) {
                        const board = matches[2];
                        let found_idx = 0;
                        let found_href = null;
                        const found_item = analyzerMap.get(board);
                        if (found_item) {
                            found_idx = found_item.index;
                            found_href = found_item.href;
                            num_found++;
                        }
                        const perm = parseInt(matches[1], 10);
                        maxPerm = Math.max(perm, maxPerm);

                        const entry: TableData = {
                            index: 0,
                            perm: perm,
                            found_idx: found_idx,
                            found_href: found_href,
                            board: board,
                            boardLines: splitBoard(board),
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
            const numEntries = tableData.length;
            setStatus(`${numEntries.toLocaleString()} unique ${ pluralize(numEntries, "solution", "solutions") } found in ${maxPerm.toLocaleString()} permutations.`);
            setNumMatches(num_found);
        } catch (err) {
            setStatus(stringifyError(err));
        }
    }

    const PIECES_ORDER = "HiWPVJLT";
    function sortPieces(arr: string[]): string[] {
        // Sort all the pieces in a specific order (matching the generator)
        const order = PIECES_ORDER.toLowerCase();
        return arr.sort((a, b) => {
            const lowerA = a.toLowerCase();
            const lowerB = b.toLowerCase();
            const firstA = order.indexOf(lowerA.charAt(0));
            const firstB = order.indexOf(lowerB.charAt(0));
            if (firstA != firstB) {
                return firstA - firstB;
            }
            if (lowerA < lowerB) {
                return -1;
            }
            if (lowerA > lowerB) {
                return 1;
            }
            return 0;
        });
    }

    function pluralize(count: number, singular: string, plural: string): string {
        return count === 1 ? singular : plural;
    }

    return (
    <>
        <div>
            <span> {status} </span>
            { numMatches < 0 ? "" : <span> {numMatches} { pluralize(numMatches, "match", "matches" ) } with <a href="../tangram/" target="_blank">analyzer</a> found.</span> }
        </div>
        <Table striped bordered hover>
            <thead>
            <tr>
                <th>#</th>
                <th>Found</th>
                <th>Preview</th>
                <th>Pieces</th>
                <th>Board</th>
            </tr>
            </thead>
            <tbody>
            {
                tableData.map((item:TableData) =>
                    <tr key={item.index} id={ `r${item.index}` }
                        className={ item.found_href ? "row-found" : "" } >
                        <td className="index">
                            <a href={ `#r${item.index}` }>{item.index}</a><br/>
                            {item.perm.toLocaleString()}
                        </td>
                        <td>{ item.found_href ? <a href={ `${TANGRAM_RELATIVE_URL}#${item.found_href}` } target="_blank">{item.found_idx}</a> : "--" }</td>
                        <td className="preview d-flex justify-content-center">
                            <BoardImageInView board={item.board} />
                        </td>
                        <td className="pieces">{item.pieces}</td>
                        <td className="board text-center">
                            {
                                item.boardLines.map((line) => (
                                    <span key={ `${item.index}-${line}"` }>{line}</span>
                                ))
                            }
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
