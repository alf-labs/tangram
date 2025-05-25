import {
    type AnchorHTMLAttributes,
    type ReactElement, useEffect, useState
} from "react";
import Markdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";
import rehypeExternalKinks from "rehype-external-links";
import introMd from "./intro.md?raw";
import rehypeSlug from "rehype-slug";


const CustomAElement: React.FC = (props: AnchorHTMLAttributes<HTMLAnchorElement>) => {
    let handleClick = undefined;
    const href = props.href ?? "";
    if (href.startsWith("#/#")) {
        handleClick = (event: any) => {
            // Process inner-page anchor jump.
            // Everything else gets the default processing.
            event.preventDefault();
            const anchor = props.href?.substring(3);
            if (anchor) {
                const element = document.getElementById(anchor);
                if (element) {
                    element.scrollIntoView({behavior: "smooth", block: "start"});
                    window.location.hash = href;
                }
            }
        }
    }
    return (
        <a href={props.href}
           onClick={handleClick}
           target={props.target}
        >
            {props.children}
        </a>
    );
}

function IntroPage() : ReactElement {
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (loading) {
            const handler = setTimeout(() => {
                jumpToAnchor();
                setLoading(false);
            }, 250); // milliseconds

            return () => {
                clearTimeout(handler);
            };
        }
    }, [loading]);

    function jumpToAnchor() {
        const match = window.location.hash.match(/#\/#(.*)$/);

        if (match) {
            const anchor = match[1];
            const element = document.getElementById(anchor);
            if (element) {
                element.scrollIntoView({behavior: "smooth", block: "start"});
            }
        }
    }

    return (
        <div className="intro-page markdown">
            <Markdown
                rehypePlugins={[
                    // support for raw (trusted) html
                    rehypeRaw,
                    // adds ids to <h1...h3>
                    rehypeSlug,
                    // add target=_blank to all external links
                    [rehypeExternalKinks, {target: "_blank", rel: []}],
                ]}
                remarkPlugins={[
                    // support for tables
                    remarkGfm,
                ]}
                components={{
                    // custom <a> handling
                    a: CustomAElement,
                }}
            >{introMd}</Markdown>
        </div>
    )
}


export default IntroPage
