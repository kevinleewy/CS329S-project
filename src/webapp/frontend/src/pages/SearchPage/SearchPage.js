import React, { useState, useEffect } from 'react';
import axios from "axios";

import { Breadcrumb, Button, Col, Row } from 'antd';
import { FileImageOutlined, ExperimentOutlined, HomeOutlined, SkinOutlined, FireOutlined } from '@ant-design/icons';
import styled from "styled-components";

import "antd/dist/antd.css"
import './styles.css';

import HeaderSteps from '../../components/Steps/Steps';
import SwipableCards from '../../components/SwipableCards/SwipableCards';
import UploadSection from '../../components/UploadSection/UploadSection';
import ProductCard from '../../components/ProductCard/ProductCard';
import { GET_RECOMMENDATIONS, RATINGS } from '../../apiPaths';



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
  text-shadow: 0 10px 10px #d1d5db;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  border-radius: 50px;
`


function SearchPage({userId}) {
  const [current, setCurrent] = useState(0);
  const [imageUrl, setImageUrl] = useState(null);
  const [searchResults, setSearchResults] = useState([]);

  const changeCurrent = (newCurrent) => {
    setCurrent(newCurrent);
  }

  const matchesPreferences = (item) => {
    const item_matches = (
      !item?.sex ||
      (item.sex === "Men" && sessionStorage.showMensClothes === "true") ||
      (item.sex === "Women" && sessionStorage.showWomensClothes === "true")
    );
    return item_matches;
  };

  useEffect(() => {
    if (current === 1) {
      axios.post(GET_RECOMMENDATIONS, {imageUrl, userId})
      .then(function (response) {
        console.log(response);
        setSearchResults([...response.data].filter(matchesPreferences));
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
      next_button: "Run Model",
      next_on_click: (() => {changeCurrent(1)}),
    },
    {
      title: 'Run Model',
      icon: (<ExperimentOutlined />),
    },
    {
      title: 'Explore Fits',
      icon: (<SkinOutlined />),
      next_button: "Rate Recommendations",
      prev_button: "Back to Upload",
      next_on_click: (() => {changeCurrent(3)}),
      prev_on_click: (() => {changeCurrent(0)}),
    },
    {
      title: 'Rate Fits',
      icon: (<FireOutlined />),
      prev_button: "Back to Upload",
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
        <div style={{display: 'block'}} className="steps-content">
          <br />
          <br />
          <br />
          <img src="https://alahausse.ca/wp-content/uploads/2021/08/giphy-phone.gif" />
        </div>
      )}
      {current === 2 && (
        <div style={{display: 'block'}} key={"slide3-${searchResults.length}imgs"} className="steps-content">
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
        <div style={{display: 'block'}} key={"slide4-${searchResults.length}imgs"}>
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
