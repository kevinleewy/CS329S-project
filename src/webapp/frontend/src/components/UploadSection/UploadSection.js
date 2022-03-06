import React, { useState } from 'react';
import axios from "axios";

import { Row, Col, Upload, message } from 'antd';
import { InboxOutlined, LoadingOutlined, PlusOutlined } from '@ant-design/icons';


const { Dragger } = Upload;

const props = {
  name: 'file',
  height: '500px',
  multiple: false,
  // action: 'https://www.mocky.io/v2/5cc8019d300000980a055e76',
  onDrop(e) {
    console.log('Dropped files', e.dataTransfer.files);
  },
  showUploadList: false,
  maxCount: 1,
};

// function getBase64(img, callback) {
//   const reader = new FileReader();
//   reader.addEventListener('load', () => callback(reader.result));
//   reader.readAsDataURL(img);
// }

function getBase64(file, callback) {
  const reader = new FileReader();
  reader.addEventListener("load", () => callback(reader.result));
  reader.readAsDataURL(file);
}

function FileUploader({fileList, setFileList, setImageUrl}) {
  const [loading, setLoading] = useState(false);

  const uploadButton = (
    <div>
      {loading ? <LoadingOutlined /> : <PlusOutlined />}
      <div style={{ marginTop: 8 }}>Upload</div>
    </div>
  );

  const onChange = (info) => {
    let fileList = [...info.fileList];
    fileList = fileList.slice(-1);
    setFileList(fileList);
    console.log("fileList:", fileList);
    setImageUrl(null);
    getBase64(fileList[0].originFileObj, setImageUrl)
    console.log("fileList:", fileList);
    
    const { status } = info.file;
    if (status !== 'uploading') {
      console.log(info.file, info.fileList);
    }
    if (status === 'done') {
      message.success(`${info.file.name} file uploaded successfully.`);
    } else if (status === 'error') {
      message.error(`${info.file.name} file upload failed.`);
    }
  }

  return (
    <Dragger {...props} onChange={onChange}>
      <p className="ant-upload-drag-icon">
        <InboxOutlined />
      </p>
      <p className="ant-upload-text">Click or drag file to this area to upload</p>
      {false && (<p className="ant-upload-hint">
        Support for a single or bulk upload. Strictly prohibit from uploading company data or other
        band files
      </p>)}
    </Dragger>
  );
}

function UploadSection({imageUrl, setImageUrl}) {
  const [fileList, setFileList] = useState([]);

  return (
    <>
      <br />
      <Row gutter={16}>
        <Col span={12}>
          <FileUploader fileList={fileList} setFileList={setFileList} setImageUrl={setImageUrl} />
        </Col>
        <Col span={12}>
          {imageUrl && (<img src={imageUrl} alt="avatar" style={{ display: "block", height: props.height, maxWidth: "100%" }} />)}
        </Col>
      </Row>
      <br />
    </>
  )
}

export default UploadSection;
