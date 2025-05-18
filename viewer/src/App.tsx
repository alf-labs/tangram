import Title from "./Title.tsx";
import TangramTable from "./TangramTable.tsx";
import {Col, Container, Row} from "react-bootstrap";
import type {ReactElement} from "react";

function App() : ReactElement {

  return (
      <Container fluid className="vh-container">
          <div className="h-100 d-flex flex-column">
              <Row className="justify-content-center">
                  <Col>
                      <Title/>
                      <p/>
                  </Col>
              </Row>
              <Row className="flex-grow-1">
                  <Col className="d-flex">
                      <TangramTable/>
                  </Col>
              </Row>
          </div>
      </Container>
)
}

export default App
