import React, { createRef, useRef, useState, useEffect } from 'react';
import axios from "axios";

import { Carousel, Layout, Menu, Breadcrumb, Steps, Button, Upload, Row, Col, message } from 'antd';
import Icon, {FileImageOutlined, ExperimentOutlined, HomeOutlined, SkinOutlined, UploadOutlined, FireOutlined, LoadingOutlined, PlusOutlined} from '@ant-design/icons';
import styled from "styled-components";

import "antd/dist/antd.css"
// import './styles.css';

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
  font-size: 28px;
  color: black;
  text-align: left;
  font-weight: bold;
`;

const Description = styled.div`
  font-size: 18px;
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

  // useEffect(() => {
  //   if (!!userId) {
  //     axios.post(GET_RECOMMENDATIONS, {userId})
  //     .then(function (response) {
  //       console.log(response);
  //       setSearchResults([...response.data]);
  //       return response.data
  //     })
  //     .catch(function (error) {
  //       console.log(error);
  //     });
  //   }
  // }, [userId]);

  
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

  const matchesPreferences = (item) => {
    const item_matches = (
      !item?.sex ||
      (item.sex === "Men" && sessionStorage.showMensClothes === "true") ||
      (item.sex === "Women" && sessionStorage.showWomensClothes === "true")
    );
    return item_matches;
  };

  useEffect(() => {
    if (!!userId) {
      axios.post(GET_RECOMMENDATIONS, {userId})
      .then(function (response) {
        console.log(response);
        setSearchResults([...response.data].filter(matchesPreferences));
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
          Personalize
        </Breadcrumb.Item>
      </Breadcrumb>
      <Title>Personalize your Recommendations</Title>
      <Description style={{marginBottom: "12px"}}>
        Swipe through a series of outfits to help us better learn your preferences and give better recommendations.
      </Description>
      <br />
      
      {(searchResults.length > 0) && (
        <div>
          <div className="site-layout-background" style={{ padding: '24px 0', minHeight: 360 }}>
            <StyledSwipableCards imgUris={searchResults.reverse().map(item => item.uri)} onSubmitRatings={onSubmitRatings} />
          </div>
        </div>
      )}
      {(searchResults.length === 0) && (
        <>
          <br />
          <br />
          <br />
          <img src="https://alahausse.ca/wp-content/uploads/2021/08/giphy-phone.gif" />
        </>
      )}
    </>
  )
}

export default SearchPage;
