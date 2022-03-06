import React, { createRef, useRef, useState, useEffect } from 'react';
import axios from "axios";

import { Carousel, Layout, Menu, Breadcrumb, Steps, Button, Upload, Row, Col, message } from 'antd';
import Icon, {FileImageOutlined, ExperimentOutlined, HomeOutlined, SkinOutlined, UploadOutlined, FireOutlined, LoadingOutlined, PlusOutlined} from '@ant-design/icons';
import styled from "styled-components";

import "antd/dist/antd.css"
import './styles.css';

import HeaderSteps from '../../components/Steps/Steps';
import SwipableCards from '../../components/SwipableCards/SwipableCards';
import UploadSection from '../../components/UploadSection/UploadSection';
import ProductCard from '../../components/ProductCard/ProductCard';
import { GET_RECOMMENDATIONS, RATINGS } from '../../apiPaths';


const { SubMenu } = Menu;
const { Header, Content, Footer, Sider } = Layout;
const { Step } = Steps;
const { Dragger } = Upload;

const Title = styled.div`
  font-size: 24px;
  color: black;
  text-align: left;
`;

const StyledSwipableCards = styled(SwipableCards)`
  background: red; // #f9fafb;
  // width: 300px;
  // height: 400px;
  // display: flex;
  // align-items: center;
  // justify-content: center;
  // flex-direction: column;
  // font-size: 150px;
  text-shadow: 0 10px 10px #d1d5db;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  border-radius: 50px;
  border: red;
  background-color: red !important;
`

const StyledUpload = styled(Upload)`
  height: 500px;
`;


function beforeUpload(file) {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
  if (!isJpgOrPng) {
    message.error('You can only upload JPG/PNG file!');
  }
  const isLt2M = file.size / 1024 / 1024 < 2;
  if (!isLt2M) {
    message.error('Image must smaller than 2MB!');
  }
  return isJpgOrPng && isLt2M;
}


function SearchPage({userId}) {
  const [collapsed, setCollapsed] = useState(false);
  const [current, setCurrent] = useState(0);
  const [imageUrl, setImageUrl] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  console.log("searchResults:", searchResults)

  // const carouselRef = useRef();
  // var carouselRef2 = null;

  const changeCurrent = (newCurrent) => {
    // carouselRef.current.goTo(newCurrent);
    setCurrent(newCurrent);
  }

  useEffect(() => {
    if (current === 1) {
      axios.post(GET_RECOMMENDATIONS, {imageUrl, userId})
      .then(function (response) {
        console.log(response);
        setSearchResults([...response.data]);
        setTimeout(() => {
          changeCurrent(2);
        }, 3000);
        return response.data
      })
      .catch(function (error) {
        console.log(error);
        changeCurrent(0);
      });
    }
  }, [current, userId]);

  const steps = [
    {
      title: 'Upload Image',
      icon: (<FileImageOutlined />),
      // content: (
      //   <UploadSection imageUrl={imageUrl} setImageUrl={setImageUrl} />
      // ),
      next_button: "Run Model",
      // next_addition: 1,
      next_on_click: (() => {changeCurrent(1)}),
    },
    {
      title: 'Run Model',
      icon: (<ExperimentOutlined />),
      // content: (
      //   <div className="site-layout-background" style={{ padding: '24px 0', minHeight: 360 }}>
      //     <StyledSwipableCards />
      //   </div>
      // ),
      // next_button: "DEBUG next",
      // next_addition: 1,
      // next_on_click: (() => {changeCurrent(2)}),
    },
    {
      title: 'Explore Fits',
      icon: (<SkinOutlined />),
      // content: (
      //   <div className="site-layout-background" style={{ padding: '24px 0', minHeight: 360 }}>
      //     <StyledSwipableCards imgs={searchResults} />
      //   </div>
      // ),
      next_button: "Rate Recommendations",
      prev_button: "Back to Upload",
      // next_addition: 1,
      // prev_addition: -2,
      next_on_click: (() => {changeCurrent(3)}),
      prev_on_click: (() => {changeCurrent(0)}),
    },
    {
      title: 'Rate Fits',
      icon: (<FireOutlined />),
      // content: (
      //   <div className="site-layout-background" style={{ padding: '24px 0', minHeight: 360 }}>
      //     <StyledSwipableCards imgs={searchResults} />
      //   </div>
      // ),
      prev_button: "Back to Upload",
      // next_addition: 1,
      // prev_addition: -3,
      prev_on_click: (() => {changeCurrent(0)}),
    },
  ];

  const [votes, setVotes] = useState(null);
  const onSubmitRatings = (votes) => {setVotes(votes)};
  const flippedSearchResults = [...searchResults].reverse();
  const imgUris = flippedSearchResults.map(item => item.uri);
  useEffect(() => {
    if (!!votes && imgUris.length === votes.length) {

      axios.post(RATINGS, {userId, votes, imageIds: flippedSearchResults.map(item => item.id)})
      .then(function (response) {
        console.log(response);
        return response.data
      })
      .catch(function (error) {
        console.log(error);
      });
    }
  }, [votes])

  useEffect(() => {
    if (!!userId) {
      axios.post(GET_RECOMMENDATIONS, {userId})
      .then(function (response) {
        console.log(response);
        setSearchResults([...response.data]);
        return response.data
      })
      .catch(function (error) {
        console.log(error);
      });
    }
  }, [userId]);

  return (
    <>
      <Breadcrumb style={{ margin: '16px 0 0', textAlign: 'left' }}>
        <Breadcrumb.Item>
          <HomeOutlined />
        </Breadcrumb.Item>
        <Breadcrumb.Item>
          Search
        </Breadcrumb.Item>
      </Breadcrumb>
      <Title style={{marginBottom: "12px"}}>Search for Outfits</Title>
      <HeaderSteps steps={steps} current={current} setCurrent={setCurrent} />
      
      {current === 0 && (
        <div style={{display: (current === 0) ? 'block' : 'none' }} className="steps-content">
          <UploadSection imageUrl={imageUrl} setImageUrl={setImageUrl} />
        </div>)
      }
      {current === 1 && (
        <div style={{display: (current === 1) ? 'block' : 'none' }} className="steps-content">
          <br />
          <br />
          <br />
          <img src="https://alahausse.ca/wp-content/uploads/2021/08/giphy-phone.gif" />
        </div>
      )}
      {current === 2 && (
        <div style={{display: (current === 2) ? 'block' : 'none' }} key={"slide3-${searchResults.length}imgs"} className="steps-content">
          <br />
          <Row gutter={[16, 16]}>
            {searchResults.map(item => (
              <Col span={4}>
                <ProductCard {...item} />
              </Col>
            ))}
          </Row>
          <br />
        </div>
      )}
      {current === 3 && (
        <div style={{display: (current === 3) ? 'block' : 'none' }} key={"slide4-${searchResults.length}imgs"}>
          <div className="site-layout-background" style={{ padding: '24px 0', minHeight: 360 }}>
            <StyledSwipableCards
              key={"slide4-swipableCards-${searchResults.length}imgs"}
              imgUris={imgUris}
              onSubmitRatings={onSubmitRatings}
            />
          </div>
        </div>
      )}
      
      <div className="steps-action" style={current !== steps.length - 1 ? {textAlign: "left"} : null}>
        {current < steps.length - 1 && steps[current].next_button && (
          <Button type="primary" onClick={steps[current].next_on_click}>
            {steps[current].next_button}
          </Button>
        )}
        {current === steps.length - 1 && steps[current].next_button && (
          <Button type="primary" onClick={steps[current].next_on_click}>
            {steps[current].next_button}
          </Button>
        )}
        {current > 0 && steps[current].prev_button && (
          <Button style={{ margin: '0 8px' }} onClick={steps[current].prev_on_click}>
            {steps[current].prev_button}
          </Button>
        )}
      </div>
    </>
  )
}

export default SearchPage;
