import { createBrowserRouter } from 'react-router';
import { Root } from './pages/Root';
import { Home } from './pages/Home';
import { ProductListing } from './pages/ProductListing';
import { ProductDetail } from './pages/ProductDetail';
import { Cart } from './pages/Cart';
import { Profile } from './pages/Profile';
import { Recommendations } from './pages/Recommendations';
import { NotFound } from './pages/NotFound';

export const router = createBrowserRouter([
  {
    path: '/',
    Component: Root,
    children: [
      {
        index: true,
        Component: Home,
      },
      {
        path: 'shop',
        Component: ProductListing,
      },
      {
        path: 'product/:id',
        Component: ProductDetail,
      },
      {
        path: 'cart',
        Component: Cart,
      },
      {
        path: 'profile',
        Component: Profile,
      },
      {
        path: 'danh-cho-ban',
        Component: Recommendations,
      },
      {
        path: '*',
        Component: NotFound,
      },
    ],
  },
]);