import {type ImgHTMLAttributes, type ReactElement, useState} from "react";
import {useInView} from "react-intersection-observer";
import {Image} from "react-bootstrap";

export function LazyImage(props: ImgHTMLAttributes<HTMLImageElement>) : ReactElement {
    const [ loaded, setLoaded ] = useState(false);
    const { ref, inView, /*entry*/ } = useInView();

    let newProps = props;
    if (!loaded) {
        if (!inView) {
            newProps = {...props};
            newProps.src = "placeholder.png";
        } else {
            setLoaded(true);
        }
    }

    return (
        <Image ref={ref} {...newProps} />
    );
}

// ~~
