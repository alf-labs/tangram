import Title from "./Title.tsx";
import TangramTable from "./TangramTable.tsx";
import {Col, Container, Row} from "react-bootstrap";
import type {ReactElement} from "react";

function App() : ReactElement {

  return (
      <Container fluid>
          <Row className="justify-content-center">
              <Col>
                  <Title/>
                  <p/>
              </Col>
          </Row>
          <Row>
              <Col>
                  <TangramTable/>
              </Col>
          </Row>
      </Container>


  )
}

export default App
