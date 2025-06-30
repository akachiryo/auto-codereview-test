# マルチステージビルドを使用してイメージサイズを最適化
FROM maven:3.9.4-eclipse-temurin-17 AS builder

# 作業ディレクトリを設定
WORKDIR /app

# pom.xmlを先にコピーして依存関係をダウンロード（キャッシュ効率化）
COPY pom.xml .

# 依存関係をダウンロード
RUN mvn dependency:go-offline

# ソースコードをコピー
COPY src ./src

# アプリケーションをビルド
RUN mvn clean package -DskipTests

# 実行用の軽量なイメージ（マルチプラットフォーム対応）
FROM eclipse-temurin:17-jre

# 作業ディレクトリを設定
WORKDIR /app

# ビルドステージからJARファイルをコピー
COPY --from=builder /app/target/*.jar app.jar

# ポート8080を公開
EXPOSE 8080

# アプリケーションを実行
ENTRYPOINT ["java", "-jar", "app.jar"] 
