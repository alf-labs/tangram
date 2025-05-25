import {type ReactElement, useEffect, useState} from "react";
import {fetchJsonFromSimpleCache} from "../SimpleCache.ts";
import {Image} from "react-bootstrap";

const PIECES_STATS_JSON_URL = "pieces_stats.json"
const PIECES_IMG_BASE_URL = "data"

interface PiecesStatsData {
    counts: PiecesCountItem[]
}

interface PiecesCountItem {
    p_key: string,      // e.g. "HR"
    f_key: string,      // e.g. "HR@000"
    key:   string,      // e.g. HR@0
    name:  string,      // e.g. "HR"
    angle: number,      // int range 0..300
    count: number,      // int
    img_path: string,   // e.g. "piece_HR@000.png"
    map_path: string,   // e.g. "piece_HR@000_map.png"
}


interface PiecesMapData {
    pieces: Map</*name*/ string, PiecesCountItem[]>
}


function PiecesPage() : ReactElement {
    const [loading, setLoading] = useState(true);
    const [status, setStatus] = useState(" ");
    const [piecesMapData, setPiecesMapData] = useState<PiecesMapData>({
        pieces: new Map<string, PiecesCountItem[]>()
    });

    useEffect(() => {
        fetchData();
    }, []);

    async function fetchData() {
        try {
            console.log("@@ Fetching pieces data");
            const piecesStatsData = await fetchJsonFromSimpleCache(PIECES_STATS_JSON_URL, PIECES_STATS_JSON_URL) as PiecesStatsData;

            console.log("@@ Process data");
            const mapData: PiecesMapData = {
                pieces: new Map<string, PiecesCountItem[]>()
            };
            for(let item of piecesStatsData.counts) {
                let list = mapData.pieces.get(item.name);
                if (list === undefined) {
                    list = [];
                    mapData.pieces.set(item.name, list);
                }
                list.push(item);
            }

            console.log("@@ Update state");
            setPiecesMapData(mapData);
            setStatus("");
            setLoading(false);
        } catch (err) {
            setStatus(stringifyError(err));
            setLoading(false);
        }
    }

    function stringifyError(error: unknown) {
        if (error instanceof Error) {
            return error.message;
        } else {
            return String(error);
        }
    }

    function generateStatusLine() {
        return <span className="pcs-status"> {status} &nbsp; </span>;
    }

    function generateDataContainer() {
        if (loading) {
            return <span className="pcs-loading">Loading...</span>;
        }

        return ( <div>
            <div className="pcs-explanation">
                <b>Heat map for every single piece</b>:
                <br/>
                For every piece (see pieces description in the <a href="#/">introduction</a>),
                this computes how frequently a piece occupies a given board cell accross
                all the board solutions.
                <br/>
                Heat map colors:
                &nbsp;
                <span style={{color: "blue"}}>&#9632;</span>&nbsp;cell not used;
                &nbsp;
                <span style={{color: "yellow"}}>&#9632;</span>..<span style={{color: "orange"}}>&#9632;</span>..<span style={{color: "red"}}>&#9632;</span>&nbsp;
                cell coverage from less to most frequent;
            </div>
            {
            Array.from(piecesMapData.pieces.values()).map( (pieces) => (
                <table className="pcs-table" key={pieces[0].name}>
                <tbody>
                    <tr className="pcs-row-title">
                        <td colSpan={pieces.length}>{pieces[0].name}</td>
                    </tr>
                    <tr className="pcs-row-pieces">
                        { pieces.map( (piece) => (
                            <td key={piece.f_key}>
                                <Image src={`${PIECES_IMG_BASE_URL}/${piece.img_path}`}></Image>
                                <div className="pcs-label">{`${piece.name}, ${piece.angle}°`}</div>
                                <Image src={`${PIECES_IMG_BASE_URL}/${piece.map_path}`}></Image>
                            </td>
                        ))}
                    </tr>
                </tbody>
                </table>
            ) ) }
        </div>
        )
    }

    return (
        <div className="pieces-page d-flex flex-column flex-grow-1">
            <div>
                {generateStatusLine()}
            </div>
            {generateDataContainer()}
        </div>
    )
}

export default PiecesPage
