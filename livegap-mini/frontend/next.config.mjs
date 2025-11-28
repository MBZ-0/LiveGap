/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: { unoptimized: true },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/videos/:path*',
        destination: 'http://localhost:8000/videos/:path*',
      },
    ];
  },
};

export default nextConfig;
