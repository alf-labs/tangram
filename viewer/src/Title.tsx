import {GIT_HASH_STR, GIT_LONG_STR} from "./GitBuild.tsx";

function Title() {

  return (
    <>
        <div className="title text-center">Tangram Generator Viewer</div>
        <div className="description text-center">
            <a href="https://github.com/alf-labs/tangram">https://github.com/alf-labs/tangram</a>
            { ", " }
            <span className="gitinfo" title={GIT_LONG_STR}>build {GIT_HASH_STR}</span>
        </div>
    </>
  )
}

export default Title
