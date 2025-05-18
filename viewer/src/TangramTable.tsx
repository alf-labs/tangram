import {type ReactElement, useEffect, useState} from "react";
import {type GridChildComponentProps, VariableSizeGrid as Grid} from "react-window";
import AutoSizer from "react-virtualized-auto-sizer";
import Table from "react-bootstrap/Table";
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
            console.log("@@ Fetching analyzer data");
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
            console.log("@@ Fetching generator data");
            const generatorData = await fetch(GENERATOR_TXT_URL);
            if (!generatorData.ok) {
                throw new Error(`Error reading data: ${generatorData.status}`);
            }
            const generatorContent = await generatorData.text();
            const tableData: TableData[] = [];
            const analyzerFound: AnalyzerItem[] = [];

            const piecesDuplicates = new Set<string>();

            console.log("@@ Parsing generator data");
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

            console.log("@@ Sorting results");
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

            console.log("@@ Indexing results");
            // Compute the index after sorting
            let index: number = 1;
            for  (const entry of tableData) {
                entry.index = index++;
            }

            console.log("@@ Update state");
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

    function generateStatusLine() {
        let line1 = <span> {status} </span>;
        let line2 = <></>;
        if (numMatches == 0) {
            line2 = <span> 0 matches with <a href="../tangram/" target="_blank">analyzer</a> found.</span>;
        } else if (numMatches > 0) {
            let a_href = tableAnalyzer[0].href;
            line2 = <span> <a
                href={`#f${a_href}`}>{numMatches} { pluralize(numMatches, "match", "matches" ) }</a> with <a
                href="../tangram/" target="_blank">analyzer</a> found.</span>;
        }

        return <>
            {line1}
            {line2}
        </>;
    }

    function generateTableRow(item: TableData) {
        let found = item.found_idx >= 0 ? tableAnalyzer[item.found_idx] : null;
        let found_prev = <></>;
        let found_link = <>--</>;
        let found_next = <></>;
        let found_id = undefined;
        if (found) {
            let found_idx = item.found_idx;
            found_id = `f${found.href}`;
            found_link = <a href={`${TANGRAM_RELATIVE_URL}#${found.href}`}
                            target="_blank">{found_idx + 1}</a>;

            if (found_idx > 0) {
                found_prev = <><a href={`#f${tableAnalyzer[found_idx - 1].href}`} className="prev">⇑ prev</a><br/></>;
            }
            if (found_idx < tableAnalyzer.length - 1) {
                found_next = <><br/><a href={`#f${tableAnalyzer[found_idx + 1].href}`} className="next">⇓ next</a></>;
            }
        }

        return <tr key={item.index} id={`r${item.index}`}
                   className={found ? "row-found" : ""}>
            <td className="index">
                <a href={`#r${item.index}`}>{item.index}</a><br/>
                {item.perm.toLocaleString()}
            </td>
            <td className="found" id={found_id}>{found_prev}{found_link}{found_next}</td>
            <td className="preview d-flex justify-content-center">
                <BoardImageInView board={item.board}/>
            </td>
            <td className="pieces">{item.pieces}</td>
            <td className="board text-center">
                {
                    item.boardLines.map((line, index) => (
                        <span key={`${item.index}-${index}"`}>{line}</span>
                    ))
                }
            </td>
        </tr>;
    }

    // New version: dynamic grid
    const columnsWidths = [100, 80, 150, 400, 100];
    const columnNames = [ "#", "Found", "Preview", "Pieces", "Board" ];
    const columnCenter = [ "", "text-center", "text-center", "", "text-center" ];
    const headHeight = 30;
    const rowHeight = 120;
    const fixedWidth = columnsWidths.reduce((acc, val) => acc + val, 0) + 20;

    function DynamicCell(cellProps: GridChildComponentProps) : ReactElement {
        const row = cellProps.rowIndex;
        const col = cellProps.columnIndex;
        if (row === 0) {
            return (
                <div className={`gridHead gridItemEven ${columnCenter[col]}`} style={cellProps.style}>
                    {columnNames[col]}
                </div>
            )
        }

        const item = tableData[row - 1];
        let content = undefined;
        let colClass = "";
        let bgColorClass = cellProps.rowIndex % 2 === 0 ? "gridItemOdd" : "gridItemEven";

        let found = item.found_idx >= 0 ? tableAnalyzer[item.found_idx] : null;
        if (found) {
            bgColorClass = "row-found";
        }

        if (col === 0) {
            colClass = "index";
            content = <>
                <a href={`#r${item.index}`}>{item.index}</a><br/>
                {item.perm.toLocaleString()}
                </>;
        } else if (col === 1) {
            colClass = "found";
            let found_prev = <></>;
            let found_link = <>--</>;
            let found_next = <></>;
            let found_id = undefined;
            if (found) {
                let found_idx = item.found_idx;
                found_id = `f${found.href}`;
                found_link = <a href={`${TANGRAM_RELATIVE_URL}#${found.href}`}
                                target="_blank">{found_idx + 1}</a>;

                if (found_idx > 0) {
                    found_prev = <><a href={`#f${tableAnalyzer[found_idx - 1].href}`} className="prev">⇑ prev</a><br/></>;
                }
                if (found_idx < tableAnalyzer.length - 1) {
                    found_next = <><br/><a href={`#f${tableAnalyzer[found_idx + 1].href}`} className="next">⇓ next</a></>;
                }
            }
            content = <div id={found_id}>{found_prev}{found_link}{found_next}</div>;
        } else if (col === 2) {
            colClass = "preview d-flex justify-content-center";
            content = <BoardImageInView board={item.board}/>;
        } else if (col === 3) {
            colClass = "pieces";
            content = <>{item.pieces}</>;
        } else if (col === 4) {
            colClass = "board";
            content = <>{
                item.boardLines.map((line, index) => (
                    <span key={`${item.index}-${index}"`}>{line}</span>
                ))
            }</>;
        }

        return (
            <div className={`gridRow ${colClass} ${bgColorClass} ${columnCenter[col]}`}
                 style={cellProps.style}>
                {content}
            </div>
        )
    }


    return (
    <div className="d-flex flex-column flex-grow-1">
        <div>
            {generateStatusLine()}
        </div>
        <div className="gridContainer">
        <AutoSizer defaultWidth={fixedWidth}>
            {({ height /*, width*/ }) => (
                    <Grid
                        width={fixedWidth}
                        height={height}
                        columnCount={5}
                        rowCount={tableData.length + 1}
                        columnWidth={index => columnsWidths[index]}
                        rowHeight={index => index === 0 ? headHeight : rowHeight}
                    >
                        {DynamicCell}
                    </Grid>
                )}
        </AutoSizer>
        </div>
    </div>
    );


    // Old version: table.
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
    );
}

export default TangramTable
