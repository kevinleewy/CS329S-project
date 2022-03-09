import React from 'react';

import { Card, Rate } from 'antd';

const { Meta } = Card;

export default function ProductCard({name, uri, price, rating, product_url}) {
  console.log(name, price, rating, product_url);
  return (
    <Card
      hoverable
      style={{ width: 240, height: 350 }}
      cover={<img alt="name" src={uri} />}
      onClick={() => window.open(product_url)}
    >
      <Meta title={price} description={""} />
      {rating && (<Rate disabled value={rating} />)}
    </Card>
  )
}
