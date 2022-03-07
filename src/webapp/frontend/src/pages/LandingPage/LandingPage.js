import React, { useState, useEffect, useRef } from 'react';
import axios from "axios";

import CircleType from "circletype";

import { Layout, Menu, Breadcrumb } from 'antd';
import Icon, {
  AppstoreOutlined,
  DesktopOutlined,
  FileOutlined,
  FireOutlined,
  HomeOutlined,
  PieChartOutlined,
  SkinOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons';
import styled from "styled-components";

import "antd/dist/antd.css"
import './styles.css';

import HeaderSteps from '../../components/Steps2/Steps';
import SwipableCards from '../../components/SwipableCards/SwipableCards';

import CatalogPage from '../CatalogPage/CatalogPage';
import SearchPage from '../SearchPage/SearchPage';
import PersonalizationPage from '../PersonalizationPage/PersonalizationPage';

import { OBTAIN_AUTH_TOKEN, AUTHENTICATE_TOKEN, GET_RECOMMENDATIONS, GUEST_ACCOUNT } from '../../apiPaths';


const { SubMenu } = Menu;
const { Header, Content, Footer, Sider } = Layout;

const Title = styled.div`
  font-size: 24px;
  color: black;
  text-align: left;
`;

const StyledSpan = styled.span`
  & div {
    position: none !important;
  }
`;

const Container = styled.div`
  & {
    height: 100vh;
    width: 100vw;
    background: white; /*#f1f1f1;*/
    background-size: cover;
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
  }
`

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

function LogoIcon() {
  return (
    <span style={{fontSize: "40px"}}>
      🧥
    </span>
  )
}

const ACCEPTED_STATUS_CODE = 200;

function LandingPage() {
  return (
    <Container className="inner">
      <div className="title" style={{zIndex: 100}}>
        🧥 FashFlix
        <div style={{fontSize: "30px", marginTop: "-20px"}}>Less Scrolling • More Possibilities • Better Outfits</div>
      </div>
      <div
        className="bottom-left"
        style={{
          height:"300px",
          width:"300px",
          borderRadius: "50%",
          zIndex: 50,
          background: "url('https://c.tenor.com/A6iXJhqsqU0AAAAC/shoes-shopping.gif')",
          backgroundSize: "cover",
        }}
      />
      <div
        className="top-right"
        style={{height:"400px", width:"400px", borderRadius: "50%", zIndex: 50}}
      />
      <img
        className="bottom"
        style={{width:"90%"}}
        src="https://static.vecteezy.com/system/resources/previews/004/113/684/original/shopping-concept-for-web-banner-woman-buys-online-shopper-makes-purchases-and-receives-online-orders-at-store-modern-people-scene-illustration-in-flat-cartoon-design-with-person-characters-vector.jpg"
      />
    </Container>
  )
}

export default LandingPage;
