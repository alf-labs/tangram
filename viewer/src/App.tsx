import Title from "./Title.tsx";
// import TangramViewer from "./TangramViewer.tsx";
import TangramTable from "./TangramTable.tsx";
import {Col, Container, Row} from "react-bootstrap";

function App() {

  return (
      <Container fluid>
          <Row className="justify-content-center">
              <Col>
                  <Title/>
                  <p/>
              </Col>
          </Row>
          {/*<Row>*/}
          {/*    <Col>*/}
          {/*        <TangramViewer/>*/}
          {/*        <p/>*/}
          {/*    </Col>*/}
          {/*</Row>*/}
          <Row>
              <Col>
                  <TangramTable/>
              </Col>
          </Row>
      </Container>


  )
}

export default App
