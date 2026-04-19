import { RouterProvider } from 'react-router';
import { router } from './routes';
import { ThemeProvider } from 'next-themes';

export default function App() {
  return (
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
      <RouterProvider router={router} />
    </ThemeProvider>
  );
}