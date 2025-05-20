import type {ReactElement} from "react";
import Markdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";
import introMd from "./intro.md?raw";

function IntroPage() : ReactElement {

    return (
        <div className="d-flex flex-column flex-grow-1 markdown">
            <Markdown rehypePlugins={[rehypeRaw, remarkGfm]}>{introMd}</Markdown>
        </div>
    )
}

export default IntroPage
