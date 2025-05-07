import {Card, Image} from "react-bootstrap";

function TangramViewer() {

  return (
    <>
        <Card className="viewer">
            <Card.Body>
                <Card.Title>Title here</Card.Title>
                <Card.Text>
                    <Image className="viewerImg" src="https://github.com/alf-labs/tangram/blob/main/analyzer/data/originals/sample/sample.jpg?raw=true" />
                    <br/>
                    Pieces:
                    <br/>
                    TW@0:5x3x0 HR@0:4x4x0 i1@0:0x1x0 P1@0:3x3x1 W1@0:2x2x0 VB@120:3x4x0 J1@240:2x2x1 L2@0:1x0x1 TO@300:4x2x0 TY@120:2x4x0 TY@180:5x4x0
                </Card.Text>
            </Card.Body>
        </Card>
    </>
  )
}

export default TangramViewer
