import {GIT_HASH_STR, GIT_LONG_STR, VERSION_MAJOR, VERSION_MINOR} from "./GitBuild.tsx";

function Title() {

  return (
    <>
        <div className="title text-center">Tangram Generator Viewer</div>
        <div className="description text-center">
            <a href="https://github.com/alf-labs/tangram" target="_blank">https://github.com/alf-labs/tangram</a>
            { `, v${VERSION_MAJOR}.${VERSION_MINOR}, ` }
            <span className="gitinfo" title={GIT_LONG_STR}>build {GIT_HASH_STR}</span>
        </div>
    </>
  )
}

export default Title
