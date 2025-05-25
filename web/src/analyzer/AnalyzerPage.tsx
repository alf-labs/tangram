import {Fragment, type ReactElement, useEffect, useState} from "react";
import {Image} from "react-bootstrap";
import {fetchJsonFromSimpleCache} from "../SimpleCache.ts";

const ANALYZER_JSON_URL = "analyzer.json"
const ANALYZER_IMG_BASE_URL = "data"
const ANALYZER_REL_URL = "#/an";

interface AnalyzerItem {
    href: string;
    index: number;
    sig: string;
    state: string; // one of "ok", "err", or "dup".
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

function AnalyzerPage(): ReactElement {
    const [loading, setLoading] = useState(true);
    const [status, setStatus] = useState(" ");
    const [analyzerData, setAnalyzerData] = useState<AnalyzerData>({
        images: [],
        stats: {
            num_img: 0,
            num_sig: 0,
            num_unique: 0,
            num_dups: 0
        },
        timestamp: ""
    });

    useEffect(() => {
        fetchData();
    }, []);

    useEffect(() => {
        if (!loading) {
            const handler = setTimeout(() => {
                setStatus(" ");
                jumpToAnchor();
            }, 250); // milliseconds

            return () => {
                clearTimeout(handler);
            };
        }
    }, [loading]);

    function jumpToAnchor() {
        const match = window.location.hash.match(/#\/an#(.*)$/);

        if (match) {
            const anchor = match[1];
            const element = document.getElementById(anchor);
            if (element) {
                element.scrollIntoView({behavior: "smooth", block: "start"});
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

    async function fetchData() {
        try {
            // Parse the analyzer data
            console.log("@@ Fetching analyzer data");
            const analyzerData = await fetchJsonFromSimpleCache(ANALYZER_JSON_URL, ANALYZER_JSON_URL) as AnalyzerData;

            console.log("@@ Update state");
            setAnalyzerData(analyzerData);
            const numEntries = analyzerData.images.length;
            setStatus(`${numEntries} ${pluralize(numEntries, "entry", "entries")} loaded.`);
            setLoading(false);
        } catch (err) {
            setStatus(stringifyError(err));
            setLoading(false);
        }
    }

    function pluralize(count: number, singular: string, plural: string): string {
        return count === 1 ? singular : plural;
    }

    function generateStatusLine() {
        return <span className="ana-status"> {status} &nbsp; </span>;
    }

    function onImageClick(event: any) {
        let img = event.target as HTMLImageElement;
        return window.open(img.src, "_blank");
    }

    function generateDataContainer() {
        if (loading) {
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
                analyzerData.images.map((item: AnalyzerItem, idx) => <Fragment key={idx}>
                    <tr className="ana-row-href" id={item.href}>
                        <td colSpan={col_spans}><a href={`${ANALYZER_REL_URL}#${item.href}`}>{`${idx + 1} - ${item.href}`}</a></td>
                    </tr>
                    <tr className={`ana-row-sig ${item.state}`}>
                        <td colSpan={col_spans}>{item.sig}</td>
                    </tr>
                    <tr className="ana-row-img">
                        <td>
                            <Image src={`${ANALYZER_IMG_BASE_URL}/${item.src}`}
                                   onClick={(event) => onImageClick(event)} />
                        </td>
                        {
                            item.alt
                                .filter((s) => s.match(img_patterns))
                                .map((url) =>
                                    <td key={`${idx}-${url}`}>
                                        <Image src={`${ANALYZER_IMG_BASE_URL}/${url}`}
                                               onClick={(event) => onImageClick(event)} />
                                    </td>
                                )
                        }
                    </tr>
                </Fragment>)
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
