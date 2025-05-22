import {type ReactElement, useEffect, useState} from "react";
import {Image} from "react-bootstrap";

const ANALYZER_JSON_URL = "analyzer.json"
const ANALYZER_IMG_BASE_URL = "data"

const LOADING_STR = "--";

interface AnalyzerItem {
    href: string;
    index: number;
    sig: string;
    src: string,
    alt: string[];
}

interface AnalyzerStats {
    num_img: number,
    num_sig: number,
    num_unique: number,
    num_dups: number,
}

interface AnalyzerData {
    images: AnalyzerItem[],
    timestamp: string,
    stats: AnalyzerStats,
}

const ALT_FILTER: string[] = [
    "_01_channels",
    "_04_hexagon",
    "_05_yrg",
    "_10_bw",
    "_11_colors",
];

function AnalyzerPage() : ReactElement {
    const [analyzerData, setAnalyzerData] = useState<AnalyzerData>( {
        images: [],
        stats: {
            num_img: 0,
            num_sig: 0,
            num_unique: 0,
            num_dups: 0
        },
        timestamp: ""
    } );
    const [status, setStatus] = useState(LOADING_STR);

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

    async function fetchData() {
        try {
            // Parse the analyzer data
            console.log("@@ Fetching analyzer data");
            const jsonData = await fetch(ANALYZER_JSON_URL);
            if (!jsonData.ok) {
                throw new Error(`Error reading data: ${jsonData.status}`);
            }
            const analyzerData = (await jsonData.json()) as AnalyzerData;

            console.log("@@ Update state");
            setAnalyzerData(analyzerData);
            const numEntries = analyzerData.images.length;
            setStatus(`${numEntries} ${ pluralize(numEntries, "entry", "entries") } loaded.`);
        } catch (err) {
            setStatus(stringifyError(err));
        }
    }

    function pluralize(count: number, singular: string, plural: string): string {
        return count === 1 ? singular : plural;
    }

    function generateStatusLine() {
        return <span className="ana-status"> {status} </span>;
    }

    function generateDataContainer() {
        if (status === LOADING_STR) {
            return <span className="ana-loading">Loading...</span>;
        }
        const img_patterns = new RegExp(ALT_FILTER.join("|"));
        const col_spans = ALT_FILTER.length + 1;

        return <table className="ana-table">
            <thead>
            </thead>
            <tbody>
            <tr className="ana-row-stats">
                <td colSpan={col_spans}><pre>
                    Analyzer output...
                    <p/>
                    |  Number of images      : {analyzerData.stats.num_img} <br/>
                    |  Processed successfully: {analyzerData.stats.num_sig} <br/>
                    |  Failed to process     : {analyzerData.stats.num_img - analyzerData.stats.num_sig} <br/>
                    |  Unique images         : {analyzerData.stats.num_unique} <br/>
                    |  Duplicated images     : {analyzerData.stats.num_dups}
                    <p/>
                    Generated on {analyzerData.timestamp}.
                </pre></td>
            </tr>
            {
                analyzerData.images.map((item: AnalyzerItem) => <>
                    <tr className="ana-row-href">
                        <td colSpan={col_spans}>{item.href}</td>
                    </tr>
                    <tr className="ana-row-sig">
                        <td colSpan={col_spans}>{item.sig}</td>
                    </tr>
                    <tr className="ana-row-img">
                        <td>
                            <Image src={`${ANALYZER_IMG_BASE_URL}/${item.src}`} />
                        </td>
                        {
                            item.alt
                                .filter((s) => s.match(img_patterns))
                                .map((url) =>
                                    <td><Image src={`${ANALYZER_IMG_BASE_URL}/${url}`} /></td>
                                )
                        }
                    </tr>
                </>)
            }
            </tbody>
        </table>;
    }

    return (
        <div className="analyzer-page d-flex flex-column flex-grow-1">
            <div>
                {generateStatusLine()}
            </div>
            {generateDataContainer()}
        </div>
    )
}

export default AnalyzerPage
