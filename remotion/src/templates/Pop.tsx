import {
  AbsoluteFill,
  Audio,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

import { BackgroundImages, TemplateProps, useCurrentCaption } from "../shared";

const ACCENT = "#FFE000";

// 잡지식/팝: 밝고 강한 톤. 상단 진행바 + 악센트 박스 자막(중앙 하단).
export const Pop = ({ audioSrc, images, captions }: TemplateProps) => {
  const caption = useCurrentCaption(captions);
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const progress = interpolate(frame, [0, durationInFrames], [0, 100], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Audio src={staticFile(audioSrc)} />
      <BackgroundImages images={images} to={1.16} />

      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.55) 100%)",
        }}
      />

      {/* 상단 진행바 */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          height: 14,
          width: `${progress}%`,
          backgroundColor: ACCENT,
        }}
      />

      {caption ? (
        <AbsoluteFill
          style={{
            justifyContent: "center",
            alignItems: "center",
            padding: "0 60px",
            marginTop: 280,
          }}
        >
          <div
            style={{
              fontFamily: "'NanumGothic', sans-serif",
              fontSize: 86,
              fontWeight: 800,
              color: "black",
              backgroundColor: ACCENT,
              padding: "16px 30px",
              borderRadius: 18,
              textAlign: "center",
              lineHeight: 1.25,
              boxShadow: "0 12px 0 rgba(0,0,0,0.28)",
            }}
          >
            {caption}
          </div>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};
