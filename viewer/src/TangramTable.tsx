import Table from 'react-bootstrap/Table';
import {Image} from "react-bootstrap";

function TangramTable() {

  return (
    <>
        <Table striped bordered hover>
            <thead>
            <tr>
                <th>#</th>
                <th>Pieces</th>
                <th>Board</th>
                <th>Board</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td id="r1"><a href="#r1">1</a></td>
                <td>TW@0:5x3x0 HR@0:4x4x0 i1@0:0x1x0 P1@0:3x3x1 W1@0:2x2x0 VB@120:3x4x0 J1@240:2x2x1 L2@0:1x0x1 TO@300:4x2x0 TY@120:2x4x0 TY@180:5x4x0</td>
                <td>
                    <div className="board text-center">
                        RRRRRRY<br/>
                        YYYYYBBYY<br/>
                        OYOOBBBBBBB<br/>
                        OOOBBBRRRRR<br/>
                        OOYYYRRRR<br/>
                        OWWWRRR
                    </div>
                </td>
                <td>
                    <Image className="previewImg" src="https://github.com/alf-labs/tangram/blob/main/analyzer/data/originals/sample/sample.jpg?raw=true" />
                </td>
            </tr>
            </tbody>
        </Table>
    </>
  )
}

export default TangramTable
