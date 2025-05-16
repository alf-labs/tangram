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
    const [tableAnalyzer, setTableAnalyzer] = useState<AnalyzerItem[]>([]);
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
            const analyzerMap: Map<string, number> = new Map();
            for (const [index, item] of analyzerList.entries()) {
                const a_item = item as AnalyzerItem;
                analyzerMap.set(a_item.sig, index);
            }

            // Parse the generator data
            const generatorData = await fetch(GENERATOR_TXT_URL);
            if (!generatorData.ok) {
                throw new Error(`Error reading data: ${generatorData.status}`);
            }
            const generatorContent = await generatorData.text();
            const tableData: TableData[] = [];
            const analyzerFound: AnalyzerItem[] = [];

            const piecesDuplicates = new Set<string>();

            setStatus("Parsing...");
            const pattern = /^@@\s+\[(\d+)]\s+SIG\s+(\S+)\s+(.+)$/;
            let maxPerm = 0;
            for (const line of generatorContent.split("\n")) {
                const matches = line.trim().match(pattern);
                if (matches) {
                    const pieces = sortPieces(matches[3].split(",")).join(" ");
                    if (!piecesDuplicates.has(pieces)) {
                        const board = matches[2];
                        let found_idx = -1;
                        let analyzerListIdx = analyzerMap.get(board) ?? -1;
                        if (analyzerListIdx >= 0) {
                            found_idx = analyzerFound.length;
                            analyzerFound.push( analyzerList[analyzerListIdx] );
                        }
                        const perm = parseInt(matches[1], 10);
                        maxPerm = Math.max(perm, maxPerm);

                        const entry: TableData = {
                            index: 0,
                            perm: perm,
                            found_idx: found_idx,
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
            setTableAnalyzer(analyzerFound);
            const numEntries = tableData.length;
            setStatus(`${numEntries.toLocaleString()} unique ${ pluralize(numEntries, "solution", "solutions") } found in ${maxPerm.toLocaleString()} permutations.`);
            setNumMatches(analyzerFound.length);
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

    function generateTableRow(item: TableData) {
        let found = item.found_idx >= 0 ? tableAnalyzer[item.found_idx] : null;
        let found_prev = <></>;
        let found_link = <>--</>;
        let found_next = <></>;
        if (found) {
            let index = item.found_idx;
            found_link = <a href={`${TANGRAM_RELATIVE_URL}#${found.href}`}
                                                          target="_blank">{index}</a>;

            if (index > 0) {
                found_prev = <><a href={`#${tableAnalyzer[index - 1].href}`}>⇑</a><br/></>;
            }
            if (index < tableAnalyzer.length - 1) {
                found_next = <><br/><a href={`#${tableAnalyzer[index + 1].href}`}>⇓</a></>;
            }
        }

        return <tr key={item.index} id={`r${item.index}`}
                   className={found ? "row-found" : ""}>
            <td className="index">
                <a href={`#r${item.index}`}>{item.index}</a><br/>
                {item.perm.toLocaleString()}
            </td>
            <td>{found_prev}{found_link}{found_next}</td>
            <td className="preview d-flex justify-content-center">
                <BoardImageInView board={item.board}/>
            </td>
            <td className="pieces">{item.pieces}</td>
            <td className="board text-center">
                {
                    item.boardLines.map((line) => (
                        <span key={`${item.index}-${line}"`}>{line}</span>
                    ))
                }
            </td>
        </tr>;
    }

    function generateStatusLine() {
        let line1 = <span> {status} </span>;
        let line2 = <></>;
        if (numMatches == 0) {
            line2 = <span> 0 matches with <a href="../tangram/" target="_blank">analyzer</a> found.</span>;
        } else if (numMatches > 0) {
            let a_href = tableAnalyzer[0].href;
            line2 = <span> <a
                href={`#r${a_href}`}>{numMatches} { pluralize(numMatches, "match", "matches" ) }</a> with <a
                href="../tangram/" target="_blank">analyzer</a> found.</span>;
        }

        return <>
            {line1}
            {line2}
        </>;
    }

    return (
    <>
        <div>
            {generateStatusLine()}
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
                tableData.map((item: TableData) => generateTableRow(item))
            }
            </tbody>
        </Table>
    </>
    )
}

export default TangramTable
