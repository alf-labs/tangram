import {useEffect, useState} from "react";
import Table from 'react-bootstrap/Table';
import {Image} from "react-bootstrap";

interface TableData {
    index: number;
    perm: number;
    found: boolean;
    pieces: string;
    board: string;
    boardLines: string[];
}

function TangramTable() {
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
            // console(`${process.env.PUBLIC_URL}`);
            const response = await fetch("/data.txt");
            if (!response.ok) {
                throw new Error(`Error reading data: ${response.status}`);
            }
            const content = await response.text();
            const tableData: TableData[] = [];

            setStatus("Parsing...");
            const pattern = /^@@\s+\[(\d+)]\s+SIG\s+(\S+)\s+(.+)$/;
            let index: number = 1;
            for (const line of content.split("\n")) {
                const matches = line.trim().match(pattern);
                console.log(JSON.stringify(matches));
                if (matches) {
                    const entry: TableData = {
                        index: index,
                        perm: parseInt(matches[1], 10),
                        found: false,
                        board: matches[2],
                        boardLines: splitBoard(matches[2]),
                        pieces: matches[3].replace(/,/g, " "),
                    }
                    tableData.push(entry);
                    index += 1;
                }
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
                    <tr>
                    <td id="r{item.index}"><a href="#r{item.index}">{item.index}</a></td>
                    <td>{item.perm}</td>
                    <td>{item.found ? "Yes" : "--"}</td>
                    <td>{item.pieces}</td>
                    <td className="board text-center">
                        {
                            item.boardLines.map((line) => (
                                <span>{line}</span>
                            ))
                        }
                    </td>
                    <td>
                        <Image className="previewImg" src="https://github.com/alf-labs/tangram/blob/main/analyzer/data/originals/sample/sample.jpg?raw=true" />
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
