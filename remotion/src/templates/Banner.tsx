import { AbsoluteFill, Audio, staticFile } from "remotion";

import { BackgroundImages, BgmTrack, TemplateProps, useCurrentCaption } from "../shared";

// 레터박스/밴드형: 영상이 중앙 밴드에 들어가고 위·아래 검은 밴드가 텍스트 캔버스.
// 상단=온스크린 헤드라인(흰색+강조색)+채널, 하단=footer(흰색+강조색). 자막은 영상 영역 안쪽 하단.
const TOP_H = 520; // 상단 검은 밴드
const BOTTOM_H = 460; // 하단 검은 밴드
const VIDEO_H = 1920 - TOP_H - BOTTOM_H; // 중앙 영상 영역

export const Banner = ({
  audioSrc,
  images,
  captions,
  bgm,
  headlineMain,
  headlineAccent,
  channelName,
  footerMain,
  footerAccent,
  accentColor = "#ff4fa3",
}: TemplateProps) => {
  const caption = useCurrentCaption(captions);
  const font = "'NanumGothic', sans-serif";
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Audio src={staticFile(audioSrc)} />
      <BgmTrack bgm={bgm} />

      {/* 중앙 영상 영역 (검은 밴드를 넘지 않음) */}
      <div
        style={{
          position: "absolute",
          top: TOP_H,
          left: 0,
          width: "100%",
          height: VIDEO_H,
          overflow: "hidden",
          backgroundColor: "#000",
        }}
      >
        <BackgroundImages images={images} to={1.08} />
        <AbsoluteFill
          style={{
            background: "linear-gradient(to bottom, rgba(0,0,0,0) 62%, rgba(0,0,0,0.72) 100%)",
          }}
        />
        {caption ? (
          <div
            style={{
              position: "absolute",
              bottom: 30,
              left: 0,
              width: "100%",
              display: "flex",
              justifyContent: "center",
              padding: "0 40px",
            }}
          >
            <div
              style={{
                fontFamily: font,
                fontSize: 48,
                fontWeight: 800,
                color: "#fff",
                background: "rgba(0,0,0,0.55)",
                padding: "8px 18px",
                borderRadius: 8,
                textAlign: "center",
                lineHeight: 1.3,
              }}
            >
              {caption}
            </div>
          </div>
        ) : null}
      </div>

      {/* 상단 밴드: 헤드라인 + 채널 */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: TOP_H,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: "0 60px",
          textAlign: "center",
        }}
      >
        {headlineMain ? (
          <div style={{ fontFamily: font, fontSize: 92, fontWeight: 900, lineHeight: 1.15, color: "#fff" }}>
            {headlineMain}
          </div>
        ) : null}
        {headlineAccent ? (
          <div style={{ fontFamily: font, fontSize: 92, fontWeight: 900, lineHeight: 1.15, color: accentColor }}>
            {headlineAccent}
          </div>
        ) : null}
        {channelName ? (
          <div style={{ marginTop: 28, fontFamily: font, fontSize: 36, fontWeight: 800, color: "#fff", opacity: 0.92 }}>
            {channelName}
          </div>
        ) : null}
      </div>

      {/* 하단 밴드: footer */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          width: "100%",
          height: BOTTOM_H,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: "0 60px",
          textAlign: "center",
          gap: 14,
        }}
      >
        {footerMain ? (
          <div style={{ fontFamily: font, fontSize: 44, fontWeight: 800, color: "#fff" }}>{footerMain}</div>
        ) : null}
        {footerAccent ? (
          <div style={{ fontFamily: font, fontSize: 44, fontWeight: 800, color: accentColor }}>{footerAccent}</div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
