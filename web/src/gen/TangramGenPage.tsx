import {type ReactElement, useEffect, useRef, useState} from "react";
import {type GridChildComponentProps, VariableSizeGrid as Grid} from "react-window";
import AutoSizer from "react-virtualized-auto-sizer";
import {BoardImageInView} from "./BoardImage.tsx";
import {Form} from "react-bootstrap";

// Data URL is relative to the public/ folder (in npm dev) or index.html (in prod).
const GENERATOR_TXT_URL = "generator.txt"
const ANALYZER_JSON_URL = "analyzer.json"
const ANALYZER_REL_URL = "#/an";
const GENERATOR_REL_URL = "#/gn";

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
    sig: string;
    state: string; // one of "ok", "err", or "dup".
    table_index: number;
}

function TangramGenPage() : ReactElement {
    const [tableData, setTableData] = useState<TableData[]>([]);
    const [tableAnalyzer, setTableAnalyzer] = useState<AnalyzerItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [status, setStatus] = useState("--");
    const [numMatches, setNumMatches] = useState(-1);
    const [showMatchesOnly, setShowMatchesOnly] = useState(false);
    const gridDataRef = useRef<Grid>(null);

    useEffect(() => {
        fetchData()
    }, [showMatchesOnly]);

    useEffect(() => {
        if (!loading) {
            const handler = setTimeout(() => {
                jumpToAnchor();
            }, 250); // milliseconds

            return () => {
                clearTimeout(handler);
            };
        }
    }, [loading]);

    function jumpToAnchor() {
        const match = window.location.hash.match(/#\/gn#[rf]([0-9]+)$/);

        if (match) {
            const anchor = match[1];
            const index = parseInt(anchor, 10);
            if (!isNaN(index)) {
                jumpToDataRow(index);
            }
        }
    }

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
            const analyzerList = (await analyzerData.json()).images;
            const analyzerMap: Map<string, number> = new Map();
            for (const [index, item] of analyzerList.entries()) {
                const a_item = item as AnalyzerItem;
                if (a_item.state == "ok" || a_item.state == "dup") {
                    analyzerMap.set(a_item.sig, index);
                }
            }

            // Parse the generator data
            console.log("@@ Fetching generator data");
            const generatorData = await fetch(GENERATOR_TXT_URL);
            if (!generatorData.ok) {
                throw new Error(`Error reading data: ${generatorData.status}`);
            }
            const generatorContent = await generatorData.text();
            let tableData: TableData[] = [];

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
                        const perm = parseInt(matches[1], 10);
                        maxPerm = Math.max(perm, maxPerm);

                        const entry: TableData = {
                            index: 0,
                            perm: perm,
                            found_idx: -1, // post-processed below
                            board: board,
                            boardLines: splitBoard(board),
                            pieces: pieces,
                        }
                        piecesDuplicates.add(pieces);
                        tableData.push(entry);
                    }
                }
            }

            // Get number of entries before filtering matches
            const numEntries = tableData.length;

            if (showMatchesOnly) {
                tableData = tableData.filter((entry) => {
                    return analyzerMap.get(entry.board) ?? -1 >= 0
                })
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
            // Compute the index after sorting, managed found items
            const analyzerFound: AnalyzerItem[] = [];
            let index: number = 1;
            for  (const entry of tableData) {
                entry.index = index++;

                let analyzerListIdx = analyzerMap.get(entry.board) ?? -1;
                if (analyzerListIdx >= 0) {
                    entry.found_idx = analyzerFound.length;
                    analyzerList[analyzerListIdx].table_index = entry.index;
                    analyzerFound.push( analyzerList[analyzerListIdx] );
                }
            }

            console.log("@@ Update state");
            setTableData(tableData);
            setTableAnalyzer(analyzerFound);
            setStatus(`${numEntries.toLocaleString()} unique ${ pluralize(numEntries, "solution", "solutions") } found in ${maxPerm.toLocaleString()} permutations.`);
            setNumMatches(analyzerFound.length);
            setLoading(false);
        } catch (err) {
            setStatus(stringifyError(err));
            setLoading(false);
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
            line2 = <span> 0 matches with <a href={ANALYZER_REL_URL}>analyzer</a> found.</span>;
        } else if (numMatches > 0) {
            let t_idx = tableAnalyzer[0].table_index;
            line2 = <span> <a
                href={`${GENERATOR_REL_URL}#f${t_idx}`}
                onClick={() => jumpToDataRow(t_idx)}>{numMatches} { pluralize(numMatches, "match", "matches" ) }</a> with <a
                href={ANALYZER_REL_URL}>analyzer</a> found.
                <Form>
                      <Form.Check // prettier-ignore
                          type="switch"
                          id="gen-show-matches"
                          label="Show matches only"
                          checked={showMatchesOnly}
                          onChange={(event) => {
                              setShowMatchesOnly(event.currentTarget.checked);
                          }}
                      />
                </Form>
            </span>;
        }

        return <div className="gen-status">
            {line1}
            {line2}
        </div>;
    }

    const columnsWidths = [100, 80, 150, 400, 100];
    const columnNames = [ "#", "Found", "Preview", "Pieces", "Board" ];
    const columnCenter = [ "", "text-center", "text-center", "", "text-center" ];
    const headHeight = 30;
    const rowHeight = 120;
    const fixedWidth = columnsWidths.reduce((acc, val) => acc + val, 0) + 20;

    function DynamicHeaderCell(cellProps: GridChildComponentProps) : ReactElement {
        const col = cellProps.columnIndex;
        return (
            <div className={`gen-grid-head gen-grid-item-even ${columnCenter[col]}`} style={cellProps.style}>
                {columnNames[col]}
            </div>
        )
    }

    function DynamicDataCell(cellProps: GridChildComponentProps) : ReactElement {
        const row = cellProps.rowIndex;
        const col = cellProps.columnIndex;
        const item = tableData[row];
        let content = undefined;
        let colClass = "";
        let bgColorClass = cellProps.rowIndex % 2 === 1 ? "gen-grid-item-odd" : "gen-grid-item-even";

        let found = item.found_idx >= 0 ? tableAnalyzer[item.found_idx] : null;
        if (found) {
            bgColorClass = "gen-row-found";
        }

        if (col === 0) {
            colClass = "gen-col-index";
            content = <>
                <a id={`r${item.index}`} href={`${GENERATOR_REL_URL}#r${item.index}`}>{item.index}</a><br/>
                {item.perm.toLocaleString()}
            </>;
        } else if (col === 1) {
            colClass = "gen-col-found";
            let found_prev = <></>;
            let found_link = <>--</>;
            let found_next = <></>;
            let found_id = undefined;
            if (found) {
                let found_idx = item.found_idx;
                found_id = `f${found.table_index}`;
                found_link = <a
                    href={`${ANALYZER_REL_URL}#${found.href}`}
                    >{found_idx + 1}</a>;

                if (found_idx > 0) {
                    let t_idx = tableAnalyzer[found_idx - 1].table_index;
                    found_prev = <><a
                        href={`${GENERATOR_REL_URL}#f${t_idx}`}
                        onClick={() => jumpToDataRow(t_idx)}
                        className="gen-found-prev">⇑ prev</a><br/></>;
                }
                if (found_idx < tableAnalyzer.length - 1) {
                    let t_idx = tableAnalyzer[found_idx + 1].table_index;
                    found_next = <><br/><a
                        href={`${GENERATOR_REL_URL}#f${t_idx}`}
                        onClick={() => jumpToDataRow(t_idx)}
                        className="gen-found-next">⇓ next</a></>;
                }
            }
            content = <div id={found_id}>{found_prev}{found_link}{found_next}</div>;
        } else if (col === 2) {
            colClass = "gen-col-preview d-flex justify-content-center";
            content = <BoardImageInView board={item.board}/>;
        } else if (col === 3) {
            colClass = "gen-col-pieces";
            content = <>{item.pieces}</>;
        } else if (col === 4) {
            colClass = "gen-col-board";
            content = <>{
                item.boardLines.map((line, index) => (
                    <span key={`${item.index}-${index}"`}>{line}</span>
                ))
            }</>;
        }

        return (
            <div className={`gen-grid-row ${colClass} ${bgColorClass} ${columnCenter[col]}`}
                 style={cellProps.style}>
                {content}
            </div>
        )
    }

    function jumpToDataRow(rowIndex: number) {
        console.log(`@@ jump to row ${rowIndex}`);
        if (gridDataRef.current) {
            gridDataRef.current.scrollToItem({
                columnIndex: 0,
                rowIndex: rowIndex,
                align: "center",
            });
        }
    }

    function generateGridDataContainer() {
        if (loading) {
            return <span className="gen-loading">Loading...</span>;
        } else {
            return <div className="gen-grid-data-container">
                <AutoSizer defaultWidth={fixedWidth}>
                    {({height /*, width*/}) => (
                        <Grid
                            ref={gridDataRef}
                            width={fixedWidth}
                            height={height}
                            columnCount={5}
                            rowCount={tableData.length}
                            columnWidth={index => columnsWidths[index]}
                            rowHeight={_index => rowHeight}
                        >
                            {DynamicDataCell}
                        </Grid>
                    )}
                </AutoSizer>
            </div>;
        }
    }

    return (
    <div className="d-flex flex-column flex-grow-1">
        <div>
            {generateStatusLine()}
        </div>
        <div className="gen-grid-header-container">
            <Grid
                width={fixedWidth}
                height={headHeight}
                columnCount={5}
                rowCount={1}
                columnWidth={index => columnsWidths[index]}
                rowHeight={_index => headHeight}
            >
                {DynamicHeaderCell}
            </Grid>
        </div>
        {generateGridDataContainer()}
    </div>
    );
}

export default TangramGenPage
