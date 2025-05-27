import {type ReactElement, useEffect, useState} from "react";
import {fetchJsonFromSimpleCache} from "../SimpleCache.ts";
import {LazyImage} from "../LazyImage.tsx";

const PIECES_STATS_JSON_URL = "pieces_stats.json"
const PIECES_IMG_BASE_URL = "data"
const PIECES_IMG_PX = 120

interface PiecesStatsData {
    counts: PiecesCountItem[],
    sums: PiecesSumsData,
}

interface PiecesCountItem {
    p_key: string,      // e.g. "HR" or "W"
    f_key: string,      // e.g. "HR@000"
    key:   string,      // e.g. HR@0
    name:  string,      // e.g. "HR" or "W1"
    angle: number,      // int range 0..300
    count: number,      // int
    img_path: string,   // e.g. "piece_HR@000.png"
    map_path: string,   // e.g. "piece_HR@000_map.png"
}

interface PiecesSumsData {
    solutions: number,  // total number of unique solutions
    pieces: { [key: string]: PiecesSumsPieceData }
}

interface PiecesSumsPieceData {
    chi: { [name: string]: number },
    rot: { [f_key: string]: number },
}

interface PiecesMapData {
    pieces: Map</*name*/ string, PiecesCountItem[]>,
    sums: { [name_or_f_key: string]: PiecesPercentData },
}

interface PiecesPercentData {
    sum: number,
    percent: number,
}

function PiecesPage() : ReactElement {
    const [loading, setLoading] = useState(true);
    const [status, setStatus] = useState(" ");
    const [piecesMapData, setPiecesMapData] = useState<PiecesMapData>({
        pieces: new Map<string, PiecesCountItem[]>(),
        sums: {},
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
                pieces: new Map<string, PiecesCountItem[]>(),
                sums: {},
            };
            for(let item of piecesStatsData.counts) {
                let list = mapData.pieces.get(item.name);
                if (list === undefined) {
                    list = [];
                    mapData.pieces.set(item.name, list);
                }
                list.push(item);

                const s = piecesStatsData.sums.pieces[item.p_key];
                const total = Math.max(1, piecesStatsData.sums.solutions);
                if (s !== undefined) {
                    const chi = Math.max(1, s.chi[item.name] ?? 1);
                    mapData.sums[item.name] = { sum: chi, percent: chi / total };
                    for(const [f_key, sum] of Object.entries(s.rot) ) {
                        mapData.sums[f_key] = { sum: sum, percent: sum / chi };
                    }
                }
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
                        <td colSpan={pieces.length}>
                            <span className="pcs-name">{pieces[0].name}</span>
                            <span className="pcs-label"
                                  title={`${piecesMapData.sums[pieces[0].name].sum} occurrences`}>
                                {`${100 * piecesMapData.sums[pieces[0].name].percent}%`}
                                {" of "}
                                {pieces[0].p_key}
                            </span>
                        </td>
                    </tr>
                    <tr className="pcs-row-pieces">
                        { pieces.map( (piece) => (
                            <td key={piece.f_key}>
                                <LazyImage src={`${PIECES_IMG_BASE_URL}/${piece.img_path}`} width={PIECES_IMG_PX} height={PIECES_IMG_PX}></LazyImage>
                                <div className="pcs-label"
                                     title={`${piecesMapData.sums[piece.f_key].sum} occurrences`}>
                                    {`${piece.name}, ${piece.angle}°`}
                                    <br/>
                                    {`${Math.round(100 * piecesMapData.sums[piece.f_key].percent)}%`}
                                </div>
                                <LazyImage src={`${PIECES_IMG_BASE_URL}/${piece.map_path}`} width={PIECES_IMG_PX} height={PIECES_IMG_PX}></LazyImage>
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
