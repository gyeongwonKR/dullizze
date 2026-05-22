import { AbsoluteFill, Audio, staticFile } from "remotion";

import { BackgroundImages, TemplateProps, useCurrentCaption } from "../shared";

// 역사/다큐: 어두운 시네마틱. 하단 그라데이션 + 비네트, 하단 중앙 자막.
export const Documentary = ({ audioSrc, images, captions }: TemplateProps) => {
  const caption = useCurrentCaption(captions);
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Audio src={staticFile(audioSrc)} />
      <BackgroundImages images={images} to={1.1} />

      {/* 이미지 통일감 + 자막 가독성을 위한 어두운 그라데이션 */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.88) 100%)",
        }}
      />

      {caption ? (
        <AbsoluteFill
          style={{
            justifyContent: "flex-end",
            alignItems: "center",
            padding: "0 70px 330px",
          }}
        >
          <div
            style={{
              fontFamily: "'NanumGothic', sans-serif",
              fontSize: 84,
              fontWeight: 800,
              color: "white",
              textAlign: "center",
              lineHeight: 1.3,
              WebkitTextStroke: "9px black",
              paintOrder: "stroke fill",
            }}
          >
            {caption}
          </div>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};
