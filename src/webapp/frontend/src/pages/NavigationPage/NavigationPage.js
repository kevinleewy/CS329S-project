import React, { useState, useEffect } from 'react';
import axios from "axios";

import { Carousel, Divider, Breadcrumb, Button, Col, Row, Form, Checkbox, Modal } from 'antd';
import {
  HomeOutlined,
  FireTwoTone,
  AppstoreTwoTone,
  SkinTwoTone,
} from '@ant-design/icons';
import styled from "styled-components";

import "antd/dist/antd.css";

import ProductCard from '../../components/ProductCard/ProductCard';
import { GET_RECOMMENDATIONS, RATINGS } from '../../apiPaths';

const Title = styled.div`
  font-size: 28px;
  color: black;
  text-align: left;
  font-weight: bold;
`;

const colors = {
  explore: {
    dark: "#00a300", //"#087830", //"#8db600", //"#52c41a",
    light: "#d0e3cc", //"#f6ffed",
  },
  rate: {
    dark: "#eb2f96",
    light: "#f6e0f6",
  },
  search: {
    dark: "#1890ff",
    light: "#e6f7ff",
  },
}

const NavigationCard = styled.div`
  background-color: white; //lightgray;
  // background: url("https://previews.123rf.com/images/teploleta/teploleta1601/teploleta160100012/50075987-seamless-black-and-white-background-with-hand-drawn-fashion-clothes-.jpg");
  // background-size: contain;
  border-radius: 8px;
  padding: 16px 40px;

  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;

  font-size: 30px;

  height: 400px;

  &:hover {
    // background-color: #1890ff;
    transform: scale(1.04);
    cursor: pointer;
  }
`;

const ExploreNavigationCard = styled(NavigationCard)`
  &:hover {
    background-color: ${colors.explore.light};
  }
`;

const RateNavigationCard = styled(NavigationCard)`
  &:hover {
    background-color: ${colors.rate.light};
  }
`;

const SearchNavigationCard = styled(NavigationCard)`
  &:hover {
    background-color: ${colors.search.light};
  }
`;

function NavigationPage({userId, setSelectedPage}) {
  const [current, setCurrent] = useState(0);
  const [imageUrl, setImageUrl] = useState(null);
  const [searchResults, setSearchResults] = useState([]);

  // var currentShowWelcomeModal = sessionStorage?.showWelcomeModal;
  // // const notSet = currentShowWelcomeModal == null
  // console.log("currentShowWelcomeModal:", currentShowWelcomeModal)
  // const [showWelcomeModal, setShowWelcomeModal] = useState((currentShowWelcomeModal == null) || currentShowWelcomeModal);
  // const handleWelcomeModalOk = (results) => {
  //   console.log("results:", results);
  //   sessionStorage.setItem("showWelcomeModal", false);
  //   setShowWelcomeModal(false);
  // }

  const [showWelcomeModal, setShowWelcomeModal] = useState(!sessionStorage?.dontShowWelcomeModal);
  const handleWelcomeModalOk = (results) => {
    console.log("results:", results);
    setShowWelcomeModal(false);
    sessionStorage.dontShowWelcomeModal = true;
    if (results.type.length === 0) {
      sessionStorage.showWomensClothes = true
    } else {
      sessionStorage.showMensClothes = results.type.indexOf("mens") !== -1;
      sessionStorage.showWomensClothes = results.type.indexOf("womens") !== -1;
    }
  }

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
      </Breadcrumb>
      <Title style={{marginBottom: "12px"}}>Welcome to FashFlix!</Title>
      <br />

      <Modal
        title="Welcome 👋"
        centered
        footer={[]}
        visible={showWelcomeModal}
      >
        <span style={{fontSize: "16px"}}>What types of clothes would you like to see?</span>
        <Form
          style={{width: "500px"}}
          onFinish={handleWelcomeModalOk}
          initialValues={{
            "type": ["womens"],
          }}
        >
          <Form.Item name="type" valuePropName="checked">
            <Checkbox.Group>
              <Checkbox value="mens" style={{ fontSize: "16px" }}>Men's</Checkbox>
              <Checkbox value="womens" style={{ fontSize: "16px" }}>Women's</Checkbox>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item style={{margin: 0}}>
            <Button type="primary" htmlType="submit">
              Confirm
            </Button>
          </Form.Item>
        </Form>
      </Modal>
      
      <Row gutter={32}>
        <Col span={8}>
          <ExploreNavigationCard onClick={() => {setSelectedPage("catalog")}}>
            <AppstoreTwoTone twoToneColor={colors.explore.dark} style={{fontSize: "40px"}} />
            <div style={{color: colors.explore.dark, fontWeight: "bold"}}>Explore</div>
            <p style={{fontSize: "20px", marginTop: "32px"}}>
              Explore products curated based on your preferences from several different online catalogs.
            </p>
          </ExploreNavigationCard>
        </Col>
        <Col span={8}>
          <RateNavigationCard onClick={() => {setSelectedPage("personalize")}}>
            <FireTwoTone twoToneColor={colors.rate.dark} style={{fontSize: "40px"}} />
            <div style={{color: colors.rate.dark, fontWeight: "bold"}}>Personalize</div>
            <p style={{fontSize: "20px", marginTop: "32px"}}>
              Swipe through a series of outfits to help us better learn your preferences and give better recommendations.
            </p>
          </RateNavigationCard>
        </Col>
        <Col span={8}>
          <SearchNavigationCard onClick={() => {setSelectedPage("search")}}>
            <SkinTwoTone twoToneColor={colors.search.dark} style={{fontSize: "40px"}} />
            <div style={{color: colors.search.dark, fontWeight: "bold"}}>Search</div>
            <p style={{fontSize: "20px", marginTop: "32px"}}>
              Have an outfit in mind? Show us a picture and we'll find fits you'll love that you can purchase now!
            </p>
          </SearchNavigationCard>
        </Col>
      </Row>

      {false && (<Carousel autoplay>
        <div>
          <div style={{textAlign: "left", fontSize: "20px"}}>Featured Items</div>
          {(searchResults.length > 0) && (
            <Row gutter={[16, 16]}>
              {[...searchResults, ...searchResults, ...searchResults, ...searchResults, ...searchResults, ...searchResults, ...searchResults].map((item, idx) => (
                <Col span={4}>
                  <ProductCard key="catalog-col-product${idx}" {...item} />
                </Col>
              ))}
            </Row>
          )}
        </div>
      </Carousel>)}
    </>
  )
}

export default NavigationPage;
