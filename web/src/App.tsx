import TangramGenPage from "./gen/TangramGenPage.tsx";
import {Container, Row} from "react-bootstrap";
import type {ReactElement} from "react";
import {HashRouter, Route, Routes} from "react-router-dom";
import IntroPage from "./intro/IntroPage.tsx";
import AppHeader from "./AppHeader.tsx";

function App() : ReactElement {

    return (
        <HashRouter>
            <AppHeader/>
            <Container fluid className="vh-container">
              <div className="h-100 d-flex flex-column">
                  <Row className="flex-grow-1">
                      <main className="col d-flex">
                          <Routes>
                              <Route path="/" element={<IntroPage />} />
                              <Route path="/gn" element={<TangramGenPage />} />
                          </Routes>
                      </main>
                  </Row>
              </div>
            </Container>
        </HashRouter>
    )
}

export default App
