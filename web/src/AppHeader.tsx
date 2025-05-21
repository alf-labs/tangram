import {GIT_HASH_STR, GIT_LONG_STR, VERSION_MAJOR, VERSION_MINOR} from "./GitBuild.tsx";
import {Nav, Navbar} from "react-bootstrap";
import {Link, useLocation} from "react-router-dom";

function AppHeader() {
    const location = useLocation();

    const isActive = (path: string) => {
        if (path === "/") {
            return location.pathname === path;
        } else {
            return location.pathname.startsWith(path);
        }
    };

  return (
    <>
        <Navbar bg="primary" data-bs-theme="dark" className="header" >
            <Navbar.Brand className="ms-3 pe-3">
                Tangram Viewer <br/>
                <span className="navbar-brand-detail">
                <a href="https://github.com/alf-labs/tangram" target="_blank">https://github.com/alf-labs/tangram/</a>
                </span>
                <span className="navbar-brand-detail">
                {`v${VERSION_MAJOR}.${VERSION_MINOR}, `}
                <span className="gitinfo" title={GIT_LONG_STR}>build {GIT_HASH_STR}</span>
                </span>
            </Navbar.Brand>
            <Nav className="me-3 flex-grow-1" variant="underline">
                <Nav.Link as={Link} to="/"   active={isActive("/"  )}>Introduction</Nav.Link>
                <Nav.Link as={Link} to="/gn" active={isActive("/gn")}>Generator</Nav.Link>
                <Nav.Link as={Link} to="/an" active={isActive("/an")}>Analyzer</Nav.Link>
                <Nav.Link as={Link} to="/pc" active={isActive("/pc")}>Pieces</Nav.Link>
            </Nav>
        </Navbar>
    </>
  )
}

export default AppHeader
