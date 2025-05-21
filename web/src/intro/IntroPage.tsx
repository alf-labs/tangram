import type {ReactElement} from "react";
import Markdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";
import introMd from "./intro.md?raw";

function IntroPage() : ReactElement {

    return (
        <div className="intro-page markdown">
            <Markdown rehypePlugins={[rehypeRaw, remarkGfm]}>{introMd}</Markdown>
        </div>
    )
}

export default IntroPage
